from .delete import delete_handling
from .put import put_handling
from .get import get_handling

from django.http import JsonResponse
import requests
import json
from os import environ
from django.conf import settings
import urllib.parse


def view_request(request, details):
    if (request.method == 'GET'):
        return get_handling(request)

    elif (request.method == 'PUT'):
        return put_handling(request, details)

    elif(request.method == 'DELETE'):
        return delete_handling(request, details)
