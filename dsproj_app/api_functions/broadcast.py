from django.http import JsonResponse
from os import environ
import requests
import json

from dsproj_app.views import get_array_views

# data = JSON
# method = PUT or DELETE
# path = stuff that comes after the IP and PORT
# filter default is none. if set, filter all IP's in it

# data = JSON
# method = PUT or DELETE
# path = stuff that comes after the IP and PORT
# filter default is none. if set, filter all IP's in it
def broadcast(data, method, path, filter=None):
	# loop = asyncio.get_event_loop()
	# loop.run_until_complete(broadcast_async(data, method, path, filter))
	# return True
    ip_addresses = get_array_views(filter)
    # ip_addresses.remove(filter)

    if method == "PUT":
        ip_addresses.remove(filter)
        for i in range(0, len(ip_addresses)):
            url = "http://" + ip_addresses[i] + path
            requests.put(url, data = data)
    elif(method == "DELETE"):
        ip_addresses.remove(filter)
        for i in range(0, len(ip_addresses)):
            url = "http://" + ip_addresses[i] + path
            requests.delete(url, data = data)
    elif( method == "GET" ):
        result = {}
        for i in range(0, len(ip_addresses)):
            url = "http://" + ip_addresses[i] + path
            response = requests.get(url, data = data)
            result[ip_addresses[i]] = response.json()
        return result
    
