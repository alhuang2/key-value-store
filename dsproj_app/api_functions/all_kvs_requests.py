from django.http import JsonResponse
from .delete import delete_handling
from .put import put_handling
from .get import get_handling
import requests
import json

# PUT/DELETE function
def keyValue_store_request(request, details, key):
    if request.method == 'PUT':
        return put_handling(request, details, key)
    elif request.method == 'DELETE':
        return delete_handling(request, details, key)
    elif request.method == 'GET' and "search" not in request.path:
        return get_handling(request, details, key)
    elif request.method == 'GET':
        return get_handling(request, details, key)
