from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from sys import getsizeof
from os import environ
from urllib.parse import parse_qs
from dsproj_app.Timestamp import Timestamp
from dsproj_app.store import Store
from dsproj_app.api_functions.all_kvs_requests import keyValue_store_request
from dsproj_app.api_functions.all_view_requests import view_request
from dsproj_app.VectorClock import VectorClock
from dsproj_app.Shards import Shards
import json

# VAR vc_position: vector clock position of current node 
vc_position = environ.get("VIEW").split(',').index(environ.get("IP_PORT"))

# VAR shards: number of shards chosen by user
shards = environ.get("S")
print("YOW MO GOW CHUO AH ", hash("peter"))
# VAR clock: vector clock object of current node
clock = VectorClock(len(environ.get("VIEW").split(',')), vc_position)

# Var store: store object of current node
store = Store()
latest_timestamp = Timestamp()
details = {
    "store": store,
    "causal_context": None,
    "clock": clock,
    "latest_timestamp": latest_timestamp
}


#ROUTE: Gets information of Node
@csrf_exempt
def node_info(request):
    info = {
        "clock": clock.get_vc(),
        "store": store.get(),
        "latest_timestamp": latest_timestamp.get_timestamp()
    }
    return JsonResponse(json.loads(json.dumps(info)), status=200, safe=False)

#ROUTE: Adds view
@csrf_exempt
def add_view(request):
    body_unicode = request.body.decode('utf-8')
    body = parse_qs(body_unicode)
    view = body['view'][0]
    environ["VIEW"] = view
    views = environ.get("VIEW").split(',')
    clock.copy_vc([0]*len(views))
    return JsonResponse(view, status=200, safe=False)

# ROUTE: GET, PUT, DELETE requests goes here
@csrf_exempt
def keyValue_store(request, key):
    return keyValue_store_request(request, details, key)

# ROUTE: VIEW requests goes here
@csrf_exempt
def view(request):
    return view_request(request, clock)

# ROUTE: Edge case for when key not provided
@csrf_exempt
def empty_put(request):
    return JsonResponse({"error": "No key provided"}, status=500)

# No need for asg4, this was used for gossip
#ROUTE: update node
@csrf_exempt
def update_node(request):
    body_unicode = request.body.decode('utf-8')
    body = parse_qs(body_unicode)
    payload = (json.loads(body['payload'][0]))['payload']

    store.copy(payload['store'])
    clock.copy_vc(payload['clock'])
    latest_timestamp.set_timestamp(payload['latest_timestamp'])
    return JsonResponse({"status": "Updated node"}, status=200)