from dsproj_app.views import get_array_views
from dsproj_app.api_functions.broadcast import broadcast
import requests
from os import environ
import json


def find_larger_vector_or_timestamp(vc_ts_k1, vc_ts_k2):
    vector1 = vc_ts_k1[0]
    vector2 = vc_ts_k2[0]
    if vector1 == vector2:
        return vc_ts_k1
    else:
        # records 2 instances where vectors
        # alternate overpowering each other's components
        bad1 = False
        bad2 = False
        for i in range(0, len(vector1)):
            if vector1[i] < vector2[i]:
                bad1 = True
            if vector1[i] > vector2[i]:
                bad2 = True

        # if 2 instances recorded, incomparable
        if (bad1 and bad2):
            # return vector2
            return find_larger_timestamp(vc_ts_k1, vc_ts_k2)
        # if self has been smaller throughout entire iteration,
        # then, v1 is not bigger
        elif bad1 == True:
            print(vector2)
            return vc_ts_k2
        # if self has been bigger througout entire iteration,
        # then, self.vs is bigger
        elif bad2 == True:
            print(vector1)
            return vc_ts_k1


def find_larger_timestamp(vc_ts1_k, vc_ts2_k):
    timestamp1 = vc_ts1_k[1]
    timestamp2 = vc_ts2_k[1]
    if timestamp1 > timestamp2:
        return vc_ts1_k
    elif timestamp2 < timestamp1:
        return vc_ts2_k
    else:
        return vc_ts1_k


def read_repair1(key, payload):
    # print("RR1 PAYLOAD", payload)
    path = "/keyValue-store/" + key
    all_info = broadcast(payload, "GET", path, environ.get("IP_PORT"))
    read_repair(all_info, key)


def read_repair(all_node_info, key):
    for each in all_node_info:
        print(all_node_info[each])
        print("")
    max = None
    all_clocks = []
    for k in all_node_info:
        print(k)
        print("")
        value = all_node_info[k]
        vc_ts_k = (value['payload']['vc'], value['payload']['tstamp'], k)
        if max == None:
            max = vc_ts_k
        else:
            max = find_larger_vector_or_timestamp(vc_ts_k, max)

    correct_vc = max[0]
    correct_ts = max[1]
    correct_ip = max[2]
    correct_payload = all_node_info[correct_ip]
    print(correct_payload)

    ip_list_to_repair = get_array_views()
    ip_list_to_repair.remove(correct_ip)

    payload = {
        "latest_timestamp": correct_ts,
        "vc": correct_vc,
        "pos": get_array_views().index(correct_ip),
        "causal_context": correct_payload['payload']['causal_context'],
        "tstamp": correct_ts
    }

    if 'val' in correct_payload:
        val = correct_payload['val']

        data = "val="+val+"&&payload="+json.dumps(payload)
        for i in range(0, len(ip_list_to_repair)):
            url = "http://" + ip_list_to_repair[i] + "/keyValue-store/" + key
            requests.put(url, data=data)
    else:
        val = None

    return val
