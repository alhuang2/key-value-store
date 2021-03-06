from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from sys import getsizeof
from os import environ
from urllib.parse import parse_qs
import json
import requests

from dsproj_app.classes.Timestamp import Timestamp
from dsproj_app.classes.VectorClock import VectorClock
from dsproj_app.classes.Store import Store
from dsproj_app.classes.Threading import Threading
from dsproj_app.classes.Rebalance import Rebalance
from dsproj_app.classes.Shards import Shards

from dsproj_app.api_functions.kvs.all_kvs_requests import keyValue_store_request
from dsproj_app.api_functions.view.all_view_requests import view_request
from dsproj_app.api_functions.api_shard_handler import shard_handler
from dsproj_app.api_functions.broadcast import broadcast


# VAR vc_position: vector clock position of current node
vc_position = environ.get("VIEW").split(",").index(environ.get("IP_PORT"))

# VAR clock: vector clock object of current node
clock = VectorClock(len(environ.get("VIEW").split(",")), vc_position)

# Var store: store object of current node
store = Store()

shards = Shards(environ.get("S"))
latest_timestamp = Timestamp()

details = {
    "store": store,
    "causal_context": None,
    "clock": clock,
    "latest_timestamp": latest_timestamp,
    "shards": shards,
}

Gossip = Threading(details, 1)
Rebalance = Rebalance(2, shards, store)
# ============= SHARD OPERATIONS =============


@csrf_exempt
def shards_api(request, route):
    return shard_handler(request, request.method, route, details)


# @csrf_exempt
# def toggle_gossip(request):
#     body_unicode = request.body.decode("utf-8")
#     body = parse_qs(body_unicode)
#     toggle = body["toggle"][0]
#     is_broadcaster = body["is_broadcaster"][0]
#     filter_ip = body["ip_filtered"][0]
#     Gossip.toggle(toggle)
#     # if is_broadcaster:
#     #     ips = environ.get("VIEW").split(",")
#     #     for ip in ips:
#     #         if ip == filter_ip:
#     #             continue
#     #         url = "http://"+ip+"/toggle_gossip"
#     #         data = {"toggle": toggle, "is_broadcaster": False, "ip_filtered": filter_ip}
#     #         requests.put(url, data=data)
#     return JsonResponse({"toggle": toggle}, status=200)


@csrf_exempt
def reset_time(request):
    latest_timestamp.set_timestamp = 0
    store.reset()
    clock.reset()
    response = {"msg": "Successfully reset node"}
    return JsonResponse(response, status=200)


@csrf_exempt
def reset_store(request, new_store):

    response = {"msg": "Successfully reset node"}
    return JsonResponse(response, status=200)


# ============= VIEW OPERATIONS =============
# ROUTE: Adds view
@csrf_exempt
def add_view(request):
    body_unicode = request.body.decode("utf-8")
    body = parse_qs(body_unicode)
    view = body["view"][0]
    environ["VIEW"] = view
    views = environ.get("VIEW").split(",")
    clock.copy_vc([0] * len(views))
    return JsonResponse(view, status=200, safe=False)


# ROUTE: VIEW requests goes here


@csrf_exempt
def view(request):
    return view_request(request, details)


# ============= KVS OPERATIONS =============
# ROUTE: GET, PUT, DELETE requests goes here


@csrf_exempt
def keyValue_store(request, key):
    return keyValue_store_request(request, details, key)


# ROUTE: Edge case for when key not provided


@csrf_exempt
def empty_put(request):
    return JsonResponse({"error": "No key provided"}, status=500)


# ============= NODE INFORMATION =============
# ROUTE: Gets information of Node


@csrf_exempt
def node_info(request):
    info = {
        "clock": clock.get_vc(),
        "store": store.get(),
        "latest_timestamp": latest_timestamp.get_timestamp(),
    }
    return JsonResponse(json.loads(json.dumps(info)), status=200, safe=False)


# No need for asg4, this was used for gossip
# ROUTE: update node


@csrf_exempt
def update_node(request):
    body_unicode = request.body.decode("utf-8")
    body = parse_qs(body_unicode)
    payload = (json.loads(body["payload"][0]))["payload"]

    # store.copy(payload['store']) # wrong use of store.copy()!!!!!!!!!!!!!!
    # payload['store'] = store.copy()
    store.overwrite_store(payload["store"])
    clock.copy_vc(payload["clock"])
    latest_timestamp.set_timestamp(payload["latest_timestamp"])
    return JsonResponse({"status": "Updated node"}, status=200)
