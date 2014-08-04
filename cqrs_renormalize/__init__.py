from rest_framework.routers import SimpleRouter
from rest_framework.viewsets import ModelViewSet

from oauth2_provider.ext.rest_framework import TokenHasReadWriteScope
from rest_framework.permissions import IsAuthenticated


def daz_update(self, request, *args, **kwargs):
    '''
    Lets paste Daryl's stuff over here for a bit...

    Once done we should just push this commoncode/django-rest-framework
    '''

    # Hackish imports just while I work on this:
    from django.core.exceptions import ObjectDoesNotExist, ValidationError

    from rest_framework import status
    from rest_framework.response import Response
    # End of hackish imports

    partial = kwargs.pop('partial', False)
    self.object = self.get_object_or_none()

    # We must work M2M serializers before execute is_valid() because it is NOT!
    data = request.DATA.copy()

    for key, value in request.DATA.iteritems():
        try:
            attr = getattr(self.object, key)
        except (AttributeError, ObjectDoesNotExist):
            continue

        # Skip loop iteration if attr is a RelatedManager
        if not hasattr(attr.__class__, 'all'):
            continue

        items = attr.model.objects.filter(pk__in=value.split(','))

        if not items.exists():
            return Response('Invalid', status=status.HTTP_400_BAD_REQUEST)

        try:
            # This only works with M2M or FK with null=True
            attr.clear()
        except AttributeError:
            # TODO how to clear ReverseFK, should we delete the objects?
            pass

        attr.add(*items)
        data.pop(key)

    serializer = self.get_serializer(
        self.object, data=data, files=request.FILES, partial=partial
    )

    # This is getting around something wrong happening in the CQRSPolyMorphic
    # from_native method.
    obj = serializer.object

    # During this call, we lose reference to the serializer.object
    # because the overridden from_native method fails to send it back
    # to us in self.errors
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        # restore the reference after its been mutated
        serializer.object = obj
        self.pre_save(serializer.object)
    except ValidationError as err:
        # full_clean on model instance may be called in pre_save,
        # so we have to handle eventual errors.
        return Response(err.message_dict, status=status.HTTP_400_BAD_REQUEST)

    if self.object is None:
        self.object = serializer.save(force_insert=True)
        self.post_save(self.object, created=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # AWESOME HAX WTF WTF
    # self.object is still the same as before. Why?

    # Something's amiss with Chris' fancy pants CQRS Auto Polymorphic
    # Serializer magix and the rabbit seems to be hiding at the bottom of the
    # hat.
    # So here, we brutally fish out the data from the request and hope that it
    # saves to hell with complex data types like DateTime...
    # I'm sure this will complain loudly at the right time.

    try:
        for key, value in data.iteritems():
            if key in ['pk', 'type']:
                continue

            print('{}: {}'.format(key, value))

            attr = getattr(self.object, key)
            klass = attr.__class__

            if hasattr(klass, 'objects'):
                kwargs = {}

                if isinstance(value, dict):
                    # if we have a dict, we have full serialized form of the
                    # object so let's do a little parsing.
                    if '_id' in value.keys():
                        # we have a mongo style _id, let's change it
                        value['id'] = value.pop('_id')

                    kwargs = value
                else:
                    # else, we're trusting that we have an id field
                    kwargs = {
                        'pk': value
                    }

                # Now let's get the instance and reassign it as value
                try:
                    value = klass.objects.get(**kwargs)
                except klass.DoesNotExist as e:
                    serializer._errors[key] = e.message

                    return Response(
                        serializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )

            setattr(self.object, key, value)

        # And what about m2m stuffs? Oh my.
        # Oh well, let's save it for now and see what breaks!
        self.object.save()

    except Exception as e:
        serializer._errors['operation'] = e.message
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    self.object = serializer.save(force_update=True)
    self.post_save(self.object, created=False)

    return Response(serializer.data, status=status.HTTP_200_OK)


def create_router_for_backend(backend):
    """
    Create a Django REST Framework router for the given CQRS/django-denormalize
    backend, mapping collection names to DRF view sets representing the
    collections.
    """

    router = SimpleRouter()

    for name, collection in backend.collections.viewitems():

        class NewViewSet(ModelViewSet):
            permission_classes = [IsAuthenticated, TokenHasReadWriteScope]

            queryset = collection.model.objects.all()
            serializer_class = collection.serializer_class

            def update(self, request, *args, **kwargs):
                # Here we call Daryl's Code to hax it!
                return daz_update(self, request, *args, **kwargs)

        NewViewSet.__name__ = collection.model.__name__ + 'ViewSet'

        router.register(name, NewViewSet)

    return router
