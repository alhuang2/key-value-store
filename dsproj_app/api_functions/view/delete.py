from django.http import JsonResponse
from os import environ
from dsproj_app.views import get_array_views, get_index_of_target_in_views
import requests
import json
import urllib.parse
from random import choice

def get_ip(request_body):
    body = request_body.decode('utf-8')
    ip_port_to_delete = body.split('=')[1]
    ip_port_to_delete = urllib.parse.unquote_plus(ip_port_to_delete)
    return ip_port_to_delete

def delete_ip(clock, ip_port_to_delete, ips):
    ip_port_array = environ.get("VIEW").split(",")
    clock.remove_vc(ip_port_array.index(ip_port_to_delete))
    
    ip_port_array.remove(ip_port_to_delete)
    environ["VIEW"] = ",".join(str(x) for x in ip_port_array)

    if ip_port_to_delete == environ.get("IP_PORT"):
        environ["VIEW"] = ip_port_to_delete

# def broadcast_delete_ip(shards, ips, ip_port_to_delete):
#     this_ip_port = environ.get("IP_PORT")
#     print("SHARD DIRECTORY: ", shards.get_directory())
#     for curr_ip_port in ips:
#         client_ip_is_not_this_ip = (
#             curr_ip_port != this_ip_port)
#         if client_ip_is_not_this_ip:
#             # set VIEW of deleted view to itself only
#             requests.delete("http://"+curr_ip_port+"/view",
#                             data='ip_port='+ip_port_to_delete)

def exchange_shards(shards, shard_id, members_of_shard_id, shard_index_of_target, ip_port_to_delete):
    requests.put("http://"+ip_port_to_delete+"/reset")
    random_node = choice(members_of_shard_id)
    shards.remove_node(shard_id, random_node)
    shards.add_node(shard_index_of_target, random_node)
    shards.remove_node(shard_index_of_target, ip_port_to_delete)

def reconstruct_shard(shards, index_to_delete, ip_port_to_delete, store):
    shard_directory = shards.get_directory()
    shard_index_of_target = index_to_delete % shards.get_shard_size()
    shard_members_of_target = shards.get_members_in_ID(shard_index_of_target)

    for shard_id, nodes in shard_directory.items():
        members_of_shard_id = shards.get_members_in_ID(shard_id)      
        
        shard_id_not_equal_to_target_shard = (shard_id != shard_index_of_target)
        current_shard_greater_than_target_shard = (len(members_of_shard_id) == len(shard_members_of_target) + 1)
                    
        if shard_id_not_equal_to_target_shard and current_shard_greater_than_target_shard:
            exchange_shards(shards, shard_id, members_of_shard_id, shard_index_of_target, ip_port_to_delete)

    target_still_in_target_shard = ip_port_to_delete in shards.get_members_in_ID(shard_index_of_target)

    if(target_still_in_target_shard):
        shards.remove_node(shard_index_of_target, ip_port_to_delete)

        if len(shards.get_members_in_ID(shard_index_of_target)) == 1:
            shards.update(shards.get_shard_size() - 1, store)


# update Shards directory by calling shards.update_view()
def delete_handling(request, details):
    clock = details['clock']
    shards = details['shards']

    body_unicode = request.body.decode('utf-8')
    body = urllib.parse.parse_qs(body_unicode)
    ip_port_to_delete = body['ip_port'][0]
    # this payload is exists to determine if client to node or node to node
    checkpoint = None
    if 'checkpoint' in body:
        checkpoint = body['checkpoint'][0]

    result_msg = ""
    msg = ""
    statuscode = 200
    number_of_shards = environ.get("S")
    ips = get_array_views()
    my_ip = environ.get("IP_PORT")
    response_content = {
        "result": "Success",
        "msg": "Successfully removed %s from view" % ip_port_to_delete
    }

    # do all the deletion stuff. aka update vc, delete ip in VIEW, etc
    # if isbroadcaster not in body:
    #   then set is_broadcaster = False
    #   set ip_port = ip_to_delete
    #   broadcast call request.delete(/view , data = checkpoint)

    if ip_port_to_delete in ips:
        index_to_delete = get_index_of_target_in_views(ip_port_to_delete)

        delete_ip(clock, ip_port_to_delete, ips)

        reconstruct_shard(shards, index_to_delete, ip_port_to_delete, details['store'])

        shards.update_view()
        shards.build_directory()

        print("views: ", environ.get("VIEW"))
        print("shard directory:", shards.get_directory())

        if checkpoint is None:
            payload_to_send = {
                "ip_port": ip_port_to_delete,
                "checkpoint": True
            }
            for ip in ips:
                if ip == my_ip:
                    continue
                url = "http://"+ip+"/view"
                requests.delete(url, data=payload_to_send)
    else:
        response_content = {
            "result": "Error",
            "msg": ip_port_to_delete + " is not in current view"
        }
        statuscode = 404

    # update vector clocks

    # update environ['view']
    # when we delete a node, update the shards directory

    # make sure it's "atomic" 


    return JsonResponse(response_content, status=statuscode)
