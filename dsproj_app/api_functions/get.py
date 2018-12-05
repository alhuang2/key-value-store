import json
from django.http import JsonResponse
from dsproj_app.api_functions.get_val_and_payload import val_and_payload
from dsproj_app.read_repair import read_repair, read_repair1
from os import environ
from dsproj_app.views import get_array_views
from dsproj_app.api_functions.broadcast import broadcast
import time

UP_TO_DATE_PAYLOAD = {}


def get_handling(request, details, key):
    store = details["store"]
    latest_timestamp = details["latest_timestamp"]
    curr_node_vc = details["clock"]
    causal_context = details["causal_context"]
    response_content = {}

    payload_json = val_and_payload(request.body)["payload_json"]

    if key == None:
        response_content = {
            "result": "Error",
            "msg": "Not provided",
            "error": "Key does not exist"
        }
        return JsonResponse(response_content, status=422)

    if "/keyValue-store/search" in request.path:
        response_content['result'] = "Success"
        response_content['payload'] = payload_json
        status = 200
        if store.is_exists(key):
            response_content['isExists'] = True
        else:
            response_content['isExists'] = False
        return JsonResponse(response_content, status=status)

    if not payload_json:  # it is empty
        IP_PORT = environ.get("IP_PORT")
        views = get_array_views()
        payload_json = {
            "vc": curr_node_vc.get_vc(),
            "pos": views.index(IP_PORT),
            "tstamp": latest_timestamp.get_timestamp(),
            "causal_context": causal_context,
        }
        causal_context = None
        data = "payload="+json.dumps(payload_json)

        read_repaired_value = read_repair1(key, data)

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
        return JsonResponse(response_content, status=status)
    else:
        views = get_array_views()
        payload_json = {
            "vc": curr_node_vc.get_vc(),
            "pos": views.index(environ.get("IP_PORT")),
            "tstamp": latest_timestamp.get_timestamp(),
            "causal_context": causal_context
        }
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
            if cc_key != None and curr_node_vc.greater_than_or_equal(payload_json["vc"]) is False:
                store.add(cc_key, "too_old", None)
                UP_TO_DATE_PAYLOAD = payload_json

            # if reading an old value, return Payload out of date,
            # remove val from response_content, and set status to 400
            if store.get_item(key)["val"] == "too_old":
                del response_content['val']
                response_content = {
                    "msg": "Payload out of date",
                    "status": 400,
                    "payload": UP_TO_DATE_PAYLOAD
                }
                return JsonResponse(response_content, status=400)

            return JsonResponse(response_content, status=200)
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
            return JsonResponse(response_content, status=status)
    return JsonResponse(response_content, status=400)
