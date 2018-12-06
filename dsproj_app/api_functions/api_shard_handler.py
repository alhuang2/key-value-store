from django.http import JsonResponse
from dsproj_app.Shards import Shards
from hashlib import sha1
import urllib.parse
import requests
import re
from json import dumps
from dsproj_app.store import Store
import random
from os import environ
from dsproj_app.views import get_array_views

# return JSON pls
def shard_handler(request, method, route, details):
    shards = details['shards']
    store = details['store']
    # route is <route>/<some_id>/<etc>
    print("route: ", route)
    if method == 'GET':
        if "my_id" in route:
            return get_id(shards)
        elif "all_ids" in route:
            return get(shards)
        elif "members" in route:
            # route = members/<id>
            return get_members_in_ID(shards, route.split('/')[1])
        elif "count" in route:
            return get_key_count_of_ID(shards, store, route.split('/')[1])
    elif method == 'PUT':
        body_unicode = request.body.decode('utf-8')
        body = urllib.parse.parse_qs(body_unicode)
        num_shards = body['num'][0]
        should_broadcast = True
        if 'broadcaster' in body:
            should_broadcast = False
        return put(shards, num_shards, store, should_broadcast)
        # GET /shard/my_id
        # GET /shard/all_ids
        # GET /shard/members/<shard_id>
        # GET /shard/count/<shard_id>
        # PUT /shard/changeShardNumber -d=”num=<number>”

        # PUT /shard/changeShardNumber -d=”num=<number>”
        # Should initiate a change in the replica groups such that the key-values are redivided
        #  across <number> groups and returns a list of all shard ids, as in GET /shard/all_ids
        # {“result”: “Success”,
        # “shard_ids”: “0,1,2”},
        # Status = 200
        # If <number> is greater than the number of nodes in the view, please return:
        # {“result”: “Error”,
        # “msg”: “Not enough nodes for <number> shards”},
        # Status = 400
        # If there is only 1 node in any partition as a result of redividing into <number> shards,
        # abort the operation and return:
        # {“result”: Error”,
        # “msg”: “Not enough nodes. <number> shards result in a nonfault tolerant shard”},
        # Status = 400
        # The only time one should have 1 node in a shard is if there is only one node in the entire system.
        # In this case it should only return an error message if you try to increase the number of shards beyond 1,
        # you should not return the second error message in this case.


def put(shards, num_shards, store, should_broadcast):
    response = shards.update(num_shards, store)
    if should_broadcast == True:
        payload_to_send = {
            "num": num_shards,
            "broadcaster": False
        }
        ips = get_array_views()
        my_ip = environ.get("IP_PORT")
        for ip in ips:
            if ip == my_ip:
                continue
            url = "http://"+ip+"/shard/changeShardNumber"
            requests.put(url, data=payload_to_send)
    status = None
    if response['is_successful']:
    	status = 200
    	return JsonResponse(response, status=status)
    else:
    	status = 400
    	return JsonResponse(response, status=status)
    	

# returns all id's
# GET /shard/my_id
# Should return the container’s shard id
# {“id”:<container’sShardId>},
# Status = 200


def get_id(shards):
    response = {
        "id": shards.get_my_shard()
    }
    return JsonResponse(response, status=200)

# return specific id
# GET /shard/all_ids
# Should return a list of all shard ids in the system as a string of comma separated values.
# {“result”: “Success”,
# “shard_ids”: “0,1,2”},
# Status = 200


def get(shards):
    response = {
        "shard_ids": shards.get_keys()
    }
    return JsonResponse(response, status=200)

# returns all the IP_PORTS associated with that shard ID
# GET /shard/members/<shard_id>
# Should return a list of all members in the shard with id <shard_id>.
# Each member should be represented as an ip-port address. (Again, the same one you pass into VIEW)
# {“result” : “Success”,
# “members”: “176.32.164.2:8080,176.32.164.3:8080”},
# Status = 200
# If the <shard_id> is invalid, please return:
# {“result”: “Error”,
# “msg”: “No shard with id <shard_id>”},
# Status = 404


def get_members_in_ID(shards, id):
    response = {}
    status = 400
    members = shards.get_members_in_ID(int(id))
    if members != None:
        members = ",".join(members)
        response = {
            "result": "Success",
            "members": members
        }
        status = 200
    else:
        response = {
            "result": "Error",
            "msg": "No shard with id " + str(id)
        }
        status = 404
    return JsonResponse(response, status=status)

# GET /shard/count/<shard_id>
# Should return the number of key-value pairs that shard is responsible for as an integer
# {“result”: “Success”,
# “Count”: <numberOfKeys> },
# Status = 200
# If the <shard_id> is invalid, please return:
# {“result”: “Error”,
# “msg”: “No shard with id <shard_id>”},
# Status = 404


def get_key_count_of_ID(shards, store, id):
    # print("not implemented yet: ", id)
    status = 404
    response = {
        "result": "Error",
        "msg": "No shard with id " + str(id)
    }
    # if it is not our current shard, request to a node
    # in that shard for their store size
    # else, we're in right shard and just return our store size
    my_shard_id = int(shards.get_my_shard())
    print("MY SHARD ID: ", my_shard_id)
    if my_shard_id == int(id):
        status = 200
        response = {
            "result": "Success",
            "Count": store.length()
        }
        return JsonResponse(response, status=status)
    else:
        members = shards.get_members_in_ID(int(id))
        if members != None:
            random_ip = random.choice(members)
            url = "http://"+random_ip+"/shard/count/"+str(id)
            print("URL TO GET COUNT : ", url)
            response = requests.get(url, data={})
            return JsonResponse(response.json(), status=response.status_code)
    # if members != None:
    # if shards.get_members_in_ID(id) != None:
    #     count = Store.kvs_size_of_shard(shards, id)
    #     response = {
    #         "result": "Success",
    #         "Count": count
    #     }
    #     status = 200
    # else:
    #     response = {
    #         "result": "Error",
    #         "msg": "No shard with id"+id
    #     }
    #     status = 404
    return JsonResponse(response, status=status)
