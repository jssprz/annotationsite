from django.shortcuts import render
from django.http import HttpResponse
from django.views.static import serve as static_serve


def cors_serve(request, path, document_root=None, show_indexes=False):
    """
    An override to `django.views.static.serve` that will allow us to add our
    own headers for development.

    Like `django.views.static.serve`, this should only ever be used in
    development, and never in production.

    Notes:
        * Taken from: https://stackoverflow.com/questions/28724951/django-dev-server-adding-headers-to-static-files
    """
    response = static_serve(request, path, document_root=document_root, show_indexes=show_indexes)

    response['Access-Control-Allow-Origin'] = '*'

    return response


def index(request):
    return HttpResponse('Hello. You\'re at the tweets index.')
