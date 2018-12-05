from django.http import JsonResponse
from os import environ
from dsproj_app.views import get_array_views, get_index_of_ip_in_views
import requests
import json
import urllib.parse
from random import choice


def delete_ip(shards, clock, ip_port_to_delete, ips):
    ip_port_array = environ.get("VIEW").split(",")
    clock.remove_vc(ip_port_array.index(ip_port_to_delete))
    ip_port_array.remove(ip_port_to_delete)
    environ["VIEW"] = ",".join(str(x) for x in ip_port_array)
    shards.update_view()


def get_ip(request_body):
    body = request_body.decode('utf-8')
    ip_port_to_delete = body.split('=')[1]
    ip_port_to_delete = urllib.parse.unquote_plus(ip_port_to_delete)
    return ip_port_to_delete


def broadcast_delete_ip(ips, ip_port_to_delete, curr_ip_port):
    if ip_port_to_delete == environ.get("IP_PORT"):
        environ["VIEW"] = ip_port_to_delete
    for curr_ip_port in ips:
        current_ip_is_not_client_ip = (
            curr_ip_port != environ.get("IP_PORT"))
        if current_ip_is_not_client_ip:
            # set VIEW of deleted view to itself only
            requests.delete("http://"+curr_ip_port+"/view",
                            data={'ip_port': ip_port_to_delete})


def reconstruct_shard(shards, index_to_delete, ip_port_to_delete, store):
    shard_directory = shards.get_directory()

    shard_index_of_target = index_to_delete % shards.get_shard_size()

    shard_members_of_target = shards.get_members_in_ID(shard_index_of_target)

    print(shard_directory)
    for shard_id, nodes in shard_directory.items():
        members_of_shard_id = shards.get_members_in_ID(shard_id)
        if len(members_of_shard_id) == len(shard_members_of_target) + 1:
            random_node = choice(members_of_shard_id)
            requests.put("http://"+ip_port_to_delete+"/reset")
            shards.remove_node(shard_id, random_node)
            shards.add_node(shard_index_of_target, random_node)
            shards.remove_node(shard_index_of_target, ip_port_to_delete)
            shards.build_directory()

    if(ip_port_to_delete in shards.get_members_in_ID(shard_index_of_target)):
        shards.remove_node(shard_index_of_target, ip_port_to_delete)
        if len(shards.get_members_in_ID(shard_index_of_target)) == 1:
            shards.update(shards.get_shard_size() - 1, store)


# update Shards directory by calling shards.update_view()
def delete_handling(request, details):
    clock = details['clock']
    shards = details['shards']
    curr_ip_port = environ.get("IP_PORT")
    
    result_msg = ""
    msg = ""
    statuscode = 200
    all_ips = urllib.parse.unquote_plus(environ.get("VIEW"))
    number_of_shards = environ.get("S")
    response_content = {}

    print("VIEWS: ", environ.get("VIEW"))
    ip_port_to_delete = get_ip(request.body)

    response_content = {
        "result": "Success",
        "msg": "Successfully removed %s from view" % ip_port_to_delete
    }

    ips = get_array_views()

    if ip_port_to_delete in ips:
        index_to_delete = get_index_of_ip_in_views(ip_port_to_delete)

        delete_ip(shards, clock, ip_port_to_delete, ips )

        reconstruct_shard(shards, index_to_delete, ip_port_to_delete, details['store'])

        broadcast_delete_ip(ips, ip_port_to_delete, curr_ip_port)
    else:
        response_content = {
            "result": "Error",
            "msg": ip_port_to_delete + " is not in current view"
        }
        statuscode = 404

    return JsonResponse(response_content, status=statuscode)
