# Actual logic for PUT/DELETE function for leader
from dsproj_app.api_functions.get_val_and_payload import val_and_payload
import requests
from django.http import JsonResponse
from sys import getsizeof
from django.views.decorators.csrf import csrf_exempt
from dsproj_app.VectorClock import VectorClock
from dsproj_app.Timestamp import Timestamp

from os import environ
from dsproj_app.api_functions.broadcast import broadcast
from ast import literal_eval
from dsproj_app.views import get_array_views
import json
import re
import urllib.parse
import time

from multiprocessing import Pool
from dsproj_app.api_functions.get_val_and_payload import val_and_payload

debug = "DEBUG====================================="

# details = []


def put_handling(request, details, key):
    store = details["store"]
    latest_timestamp = details["latest_timestamp"]
    curr_node_vc = details["clock"]
    causal_context = details["causal_context"]

    response_content = {}
    if len(request.body) <= 0:
        response_content['msg'] = 'Error'
        response_content['result'] = 'Error'
        response_content['error'] = 'Value is missing'
        return JsonResponse(response_content, status=422)

    if (0 < len(key) > 200):
        response_content['msg'] = 'Error'
        response_content['result'] = 'Error'
        response_content['error'] = 'Key not valid'
        return JsonResponse(response_content, status=422)

    payload_json = val_and_payload(request.body)["payload_json"]
    val = val_and_payload(request.body)["val"]

    if payload_json:  # not empty
        req_vc = payload_json['vc']
        req_timestamp = payload_json['tstamp']
        if 'latest_timestamp' in payload_json and latest_timestamp.get_timestamp() == None:
            latest_timestamp.set_timestamp(payload_json['latest_timestamp'])
        else:
            lt = latest_timestamp.max_timestamp(req_timestamp)
            latest_timestamp.set_timestamp(lt)
        req_position = int(payload_json['pos'])
    else:
        curr_node_vc.increment_self()
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
        causal_context = None

    ##########################################################
    # IF SIZE OF OBJECT UPLOADED GREATER THAN PERMITTED SIZE #
    ##########################################################
    if getsizeof(val) > 1024:
        response_content['result'] = 'Error'
        response_content['msg'] = 'Object too large. Size limit is 1MB'
        response_content['error'] = 'Key not valid'
        return JsonResponse(response_content, status=422)

    payload_json['vc'] = curr_node_vc.get_vc()
    # Case: 'subject' does not exist
    if not store.has_key(key):
        response_content['replaced'] = False
        response_content['msg'] = 'Added successfully'
        response_content['payload'] = payload_json
        status = 200

    # Case: 'subject' existsupdated_payload_and_sender
    elif store.has_key(key):
        response_content['replaced'] = True
        response_content['msg'] = 'Updated successfully'
        response_content['payload'] = payload_json
        status = 201

    store.add(key, val, payload_json["causal_context"])

    # print("DEBUG================()()()============================")
    # print(curr_node_vc.get_vc())
    # print(payload_json['tstamp'])
    # print("============================================")

    return JsonResponse(response_content, status=status)
