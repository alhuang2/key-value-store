from django.http import JsonResponse
from os import environ
from dsproj_app.views import get_array_views, get_index_of_ip_in_views
import requests
import json
import urllib.parse


def delete_ip(request_body, ip_port_to_delete):
    if ip_port_to_delete not in environ.get("VIEW"):
        return False

    ip_port_array = environ.get("VIEW").split(",")
    clock.remove_vc(ip_port_array.index(ip_port_to_delete))
    ip_port_array.remove(ip_port_to_delete)
    environ["VIEW"] = ",".join(str(x) for x in ip_port_array)
    return True


def get_ip(request_body):
    body = request_body.decode('utf-8')
    ip_port_to_delete = body.split('=')[1]
    ip_port_to_delete = urllib.parse.unquote_plus(ip_port_to_delete)
    return ip_port_to_delete


def remove_ip(ips, ip_port_to_delete, curr_ip_port):
    if ip_port_to_delete == environ.get("IP_PORT"):
        environ["VIEW"] = ip_port_to_delete
    for curr_ip_port in ips:
        current_ip_is_not_client_ip = (
            curr_ip_port != environ.get("IP_PORT"))
        if current_ip_is_not_client_ip:
            # set VIEW of deleted view to itself only
            requests.delete("http://"+curr_ip_port+"/view",
                            data={'ip_port': ip_port_to_delete})


def reconstruct_shard(shards, ip_port_to_delete):
    shard_directory = shards.get_directory()

    shard_index_of_target = get_index_of_ip_in_views(
        ip_port_to_delete) % shards.get_shard_size()

    shard_members_of_target = shards.get_members_in_ID(shard_index_of_target)

    for shard_id, nodes in shard_directory.iteritems():
        members_of_shard_id = shards.get_members_in_ID(shard_id)
        if len(members_of_shard_id) == len(shard_members_of_target) + 1:
            random_node = random.choice(members_of_shard_id)
            # is this where you re-distribute / rehash everything?
            requests.put("http://"+ip_port_to_delete+"/reset")
            shards.remove_node(shard_id, random_node)
            shards.add_node(shard_index_of_target, random_node)
            shards.remove_node(shard_index_of_target, ip_port_to_delete)

    if(ip_port_to_delete in shards.get_members_in_ID(shard_index_of_target)):
        shards.remove_node(shard_index_of_target, ip_port_to_delete)
        if len(shards.get_members_in_ID(shard_index_of_target)) == 1:
            shards.update_shard_size(len(shard_directory) - 1)
            lonely_node = shards.get_members_in_ID(shard_index_of_target)[0]
            shards.remove_node(shard_index_of_target, lonely_node)

            new_node_index = get_index_of_ip_in_views(
                lonely_node) % shards.get_shard_size()

            shards.add_node(new_node_index, lonely_node)


def delete_handling(request, details):
    clock = details['clock']
    shards = details['shards']
    result_msg = ""
    msg = ""
    statuscode = 200
    all_ips = urllib.parse.unquote_plus(environ.get("VIEW"))
    number_of_shards = environ.get("S")
    response_content = {}

    ip_port_to_delete = get_ip(request.body)

    response_content = {
        "result": "Success",
        "msg": "Successfully removed %s from view" % ip_port_to_delete
    }

    reconstruct_shard(shards, ip_port_to_delete)

    is_exists = delete_ip(request.body, ip_port_to_delete)
    if is_exists:
        remove_ip(all_ips.split(","), ips, ip_port_to_delete, curr_ip_port)
    else:
        response_content = {
            "result": "Error",
            "msg": ip_port_to_delete + " is not in current view"
        }
        statuscode = 404

    return JsonResponse(response_content, status=statuscode)
