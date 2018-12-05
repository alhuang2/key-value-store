from django.http import JsonResponse
from os import environ


def get_handling(request):
    view_string = environ.get("VIEW")
    return JsonResponse({"view": view_string}, status=200)
