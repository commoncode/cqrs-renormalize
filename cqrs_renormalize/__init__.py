from rest_framework.viewsets import ModelViewSet
from rest_framework.routers import SimpleRouter


def create_router_for_backend(backend):
    """
    Create a Django REST Framework router for the given CQRS/django-denormalize
    backend, mapping collection names to DRF view sets representing the
    collections.
    """

    router = SimpleRouter()

    for name, collection in backend.collections.viewitems():

        class NewViewSet(ModelViewSet):
            queryset = collection.model.objects.all()
            serializer_class = collection.serializer_class

        NewViewSet.__name__ = collection.model.__name__ + 'ViewSet'

        router.register(name, NewViewSet)

    return router