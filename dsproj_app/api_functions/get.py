import json
from django.http import JsonResponse
from dsproj_app.api_functions.get_val_and_payload import val_and_payload
from os import environ
from dsproj_app.views import get_array_views
from hashlib import sha1
import random
import requests

UP_TO_DATE_PAYLOAD = {}

def get_handling(request, details, key):
    store = details["store"]
    latest_timestamp = details["latest_timestamp"]
    curr_node_vc = details["clock"]
    causal_context = details["causal_context"]
    shards = details["shards"]
    response_content = {}

    payload_json = val_and_payload(request.body)["payload_json"]

    # OPTION: NO KEY PROVIDED
    if key == None:
        response_content = {
            "result": "Error",
            "msg": "Not provided",
            "error": "Key does not exist"
        }
        return JsonResponse(response_content, status=422)

    # OPTION: SEARCH-GET
    if "/keyValue-store/search" in request.path:
        response_content['result'] = "Success"
        response_content['payload'] = payload_json
        if store.is_exists(key):
            response_content['isExists'] = True
        else:
            response_content['isExists'] = False
        return JsonResponse(response_content, status=200)
    
    # OPTION: EMPTY PAYLOAD (USER REQUEST), HASH KEY AND CHECK SHARD DIRECTORY
    if not payload_json:
        payload_json = {
            "vc": curr_node_vc.get_vc(),
            "pos": get_array_views().index(environ.get("IP_PORT")),
            "tstamp": latest_timestamp.get_timestamp(),
            "causal_context": causal_context,
        }
        causal_context = None
        data = "payload="+json.dumps(payload_json)


        if store.is_exists(key):
            response_content = {
                "result": "Success",
                "val": store.get_item(key)['val'],
                "payload": payload_json
            }
            status = 200
        else:
            response_content = {
                "result": "Error",
                "msg": "Key does not exist",
                "payload": payload_json
            }
            status = 404

        shard_location = None
        binary_key = sha1(key.encode())
        shard_location = int(binary_key.hexdigest(), 16) % shards.get_shard_size()

        # OPTION: WE'RE IN THE WRONG SHARD, REDIRECT REQUEST TO NODE WITH CORRECT SHARD
        current_node_not_in_shard = not (environ.get("IP_PORT") in shards.get_members_in_ID(shard_location))
        response_content["owner"] = shards.get_my_shard()
        if (current_node_not_in_shard):
            members = shards.get_members_in_ID(shard_location)
            if members != None:
                rand_address = random.choice(members)
                response = requests.get("http://"+rand_address+"/keyValue-store/"+key, data="payload="+json.dumps(payload_json))
                return JsonResponse(response.json(), status=response.status_code)
            else:
                response_content = {
                    "result": "Error",
                    "msg": "No nodes in shard " + shard_location,
                    "payload": payload_json                
                }
                status = 400
                return JsonResponse(response_content, status=status)
        else:
            return JsonResponse(response_content, status=status)

    # OPTION: NON-EMPTY PAYLOAD (NODES COMMUNICATING). WE'RE IN THE
    # RIGHT CONTAINER, JUST DO NORMAL GET
    else:
        views = get_array_views()
        payload_json = {
            "vc": curr_node_vc.get_vc(),
            "pos": views.index(environ.get("IP_PORT")),
            "tstamp": latest_timestamp.get_timestamp(),
            "causal_context": causal_context
        }

        # CONDITION: If store already has the key 
        if store.is_exists(key):
            causal_context = {
                "key": key,
                "vc": curr_node_vc.get_vc()
            }
            response_content['result'] = "Success"
            response_content['val'] = store.get_item(key)['val']

            payload_json['value'] = store.get_item(key)['val']
            response_content['payload'] = payload_json
            cc_key = store.get_item(key)["causal_context"]

            # CONDITION: If causal context exists and requestor's vc > this vc 
            if cc_key != None and curr_node_vc.greater_than_or_equal(payload_json["vc"]) is False:
                store.add(cc_key, "too_old", None)
                UP_TO_DATE_PAYLOAD = payload_json

            # CONDITION: if reading an old value, return Payload out of date,
            # remove val from response_content, and set status to 400
            if store.get_item(key)["val"] == "too_old":
                del response_content['val']
                response_content = {
                    "msg": "Payload out of date",
                    "status": 400,
                    "payload": UP_TO_DATE_PAYLOAD
                }
                status = 400
            status = 200
        else:
            payload_json = {
                "value": None,
                "vc": curr_node_vc.get_vc(),
                "pos": views.index(environ.get("IP_PORT")),
                "tstamp": latest_timestamp.get_timestamp(),
                "causal_context": causal_context
            }
            response_content['payload'] = payload_json
            status = 404
        response_content["owner"] = shards.get_my_shard()
    return JsonResponse(response_content, status=status)