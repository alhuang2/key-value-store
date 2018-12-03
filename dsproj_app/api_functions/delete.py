from django.http import JsonResponse
from dsproj_app.api_functions.get_val_and_payload import val_and_payload
from os import environ
import time
from dsproj_app.views import get_array_views


def delete_handling(request, details, key):
    store = details["store"]
    latest_timestamp = details["latest_timestamp"]
    curr_node_vc = details["clock"]
    causal_context = details["causal_context"]

    response_content = {}

    # OPTION: NO KEY PROVIDED
    if key is None:
        response_content['result'] = 'Error'
        response_content['msg'] = 'Not provided'
        return JsonResponse(response_content, status=422)

    payload_json = val_and_payload(request.body)["payload_json"]

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
        IP_PORT = environ.get("IP_PORT")
        views = get_array_views()
        req_vc = curr_node_vc.get_vc()
        req_position = views.index(IP_PORT)
        req_timestamp = time.time()
        if latest_timestamp.get_timestamp() == None:
            latest_timestamp.set_timestamp(req_timestamp)
            payload_json['latest_timestamp'] = latest_timestamp.get_timestamp()
        payload_json['vc'] = req_vc
        payload_json['pos'] = req_position
        payload_json['tstamp'] = req_timestamp
        payload_json['causal_context'] = causal_context
        causal_context = None
    status = 200

    # OPTION: KEY DELETED
    if not store.has_key(key) or store.get()[key]['tombstone'] == True:
        response_content['result'] = "Error"
        response_content['msg'] = "Key does not exist"
        response_content['payload'] = payload_json
        status = 404

    # OPTION: KEY EXISTS, SUCCESSFULLY DELETED
    else:
        response_content['result'] = "Success"
        response_content['msg'] = "Key deleted"
        response_content['payload'] = payload_json
        store.delete_key(key)
    curr_node_vc.increment_index(req_position)

    return JsonResponse(response_content, status=status)
