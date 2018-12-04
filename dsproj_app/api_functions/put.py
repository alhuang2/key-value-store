# Actual logic for PUT/DELETE function for leader
from dsproj_app.api_functions.get_val_and_payload import val_and_payload
from django.http import JsonResponse
from sys import getsizeof
from os import environ
from dsproj_app.views import get_array_views
from hashlib import sha1
import json
import re
import urllib.parse
import time
import requests
import random


def put_handling(request, details, key):
    store = details["store"]
    latest_timestamp = details["latest_timestamp"]
    curr_node_vc = details["clock"]
    causal_context = details["causal_context"]
    shards = details["shards"]
    response_content = {}

    # OPTION: VALUE MISSING
    if len(request.body) <= 0:
        response_content['msg'] = 'Error'
        response_content['result'] = 'Error'
        response_content['error'] = 'Value is missing'
        return JsonResponse(response_content, status=422)

    # OPTION: KEY LENGTH INVALID
    if (0 < len(key) > 200):
        response_content['msg'] = 'Error'
        response_content['result'] = 'Error'
        response_content['error'] = 'Key not valid'
        return JsonResponse(response_content, status=422)


    payload_json = val_and_payload(request.body)["payload_json"]
    val = val_and_payload(request.body)["val"]

    # OPTION: VALUE SIZE TOO BIG
    if getsizeof(val) > 1024:
        response_content['result'] = 'Error'
        response_content['msg'] = 'Object too large. Size limit is 1MB'
        response_content['error'] = 'Key not valid'
        return JsonResponse(response_content, status=422)

    shard_location = None
    print("Before: ", payload_json)

    # OPTION: KEY NEVER EXISTED
    if not store.has_key(key):
        response_content['replaced'] = False
        response_content['msg'] = 'Added successfully'
        response_content['payload'] = payload_json
        status = 200

    # OPTION: KEY ALREADY EXISTS AND IS BEING REPLACED
    elif store.has_key(key):
        response_content['replaced'] = True
        response_content['msg'] = 'Updated successfully'
        response_content['payload'] = payload_json
        status = 201

    # OPTION: NON-EMPTY PAYLOAD (NODES COMMUNICATING)
    if payload_json:
        req_vc = payload_json['vc']
        req_timestamp = payload_json['tstamp']
        if 'latest_timestamp' in payload_json and latest_timestamp.get_timestamp() == None:
            latest_timestamp.set_timestamp(payload_json['latest_timestamp'])
        else:
            lt = latest_timestamp.max_timestamp(req_timestamp)
            latest_timestamp.set_timestamp(lt)
        req_position = int(payload_json['pos'])

    # OPTION: EMPTY PAYLOAD (USER REQUEST)
    else:
        # curr_node_vc.increment_self()
        IP_PORT = environ.get("IP_PORT")
        views = get_array_views()
        req_vc = curr_node_vc.get_vc()
        req_position = views.index(IP_PORT)
        req_timestamp = time.time()
        if latest_timestamp.get_timestamp() == None:
            latest_timestamp.set_timestamp(req_timestamp)
            payload_json['latest_timestamp'] = latest_timestamp.get_timestamp()
        # payload_json['vc'] = req_vc
        payload_json['pos'] = req_position
        payload_json['tstamp'] = req_timestamp
        payload_json['causal_context'] = causal_context
        payload_json['vc'] = req_vc
        causal_context = None
        binary_key = sha1(key.encode())
        shard_location = int(binary_key.hexdigest(), 16) % shards.get_shard_size()


    # OPTION: KEY NEVER EXISTED
    if not store.has_key(key):
        response_content['replaced'] = False
        response_content['msg'] = 'Added successfully'
        response_content['payload'] = payload_json
        status = 200

    # OPTION: KEY ALREADY EXISTS AND IS BEING REPLACED
    elif store.has_key(key):
        response_content['replaced'] = True
        response_content['msg'] = 'Updated successfully'
        response_content['payload'] = payload_json
        status = 201
        
    # if in right shard
    if (shard_location != None and not (environ.get("IP_PORT") in shards.get_members_in_ID(shard_location))):
        members = shards.get_members_in_ID(shard_location)
        if members != None:
            rand_address = random.choice(members)
            data = "val="+val+"&&payload="+json.dumps(payload_json)
            response = requests.put("http://"+rand_address+"/keyValue-store/"+key, data=data)
            return JsonResponse(response.json(), status = response.status_code)
        else:
            response_content = {
                "result": "Error",
                "msg": "No nodes in shard " + shard_location,
                "payload": payload_json                
            }
            status = 400
            return JsonResponse(response_content, status=status)
    # if in wrong shard
    else:
        curr_node_vc.increment_self() 
        payload_json['vc'] = curr_node_vc.get_vc()       
        store.add(key, val, payload_json["causal_context"])
        print("I AM ADDING KEY")
        response_content["owner"] = shards.get_my_shard()
        return JsonResponse(response_content, status=status)


    return JsonResponse(response_content, status=status)
