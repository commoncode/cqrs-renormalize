from setuptools import setup, find_packages

setup( name='cqrs-renormalize',
    version = '0.0.1',
    description = 'Endpoints for creating/viewing/updating/deleting data from the serialized forms',
    author = 'Chris Morgan',
    author_email = 'chris@commoncode.com.au',
    url = 'https://github.com/commoncode/cqrs-renormalize',
    keywords = ['django',],
    packages = find_packages(),
    include_package_data = True,
    zip_safe = False,
    classifiers = [
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    # dependency_links = [
    #     'http://github.com/commoncode/cqrs/tarball/master#egg=cqrs-0.0.1',
    # ],
    # install_requires = [
    #     'django-denormalize',
    #     'djangorestframework',
    #     'cqrs',
    # ],
)
