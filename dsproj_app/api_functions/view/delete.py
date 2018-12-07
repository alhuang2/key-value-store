from django.http import JsonResponse
from os import environ
from dsproj_app.views import get_array_views, get_index_of_target_in_views
import requests
import json
import urllib.parse
from random import choice


def get_ip(request_body):
    body = request_body.decode("utf-8")
    ip_port_to_delete = body.split("=")[1]
    ip_port_to_delete = urllib.parse.unquote_plus(ip_port_to_delete)
    return ip_port_to_delete


def delete_ip(clock, ip_port_to_delete, ips):
    ip_port_array = environ.get("VIEW").split(",")
    clock.remove_vc(ip_port_array.index(ip_port_to_delete))

    ip_port_array.remove(ip_port_to_delete)
    environ["VIEW"] = ",".join(str(x) for x in ip_port_array)

    if ip_port_to_delete == environ.get("IP_PORT"):
        environ["VIEW"] = ip_port_to_delete

    shards.update_view()


def exchange_shards(
    shards, shard_id, members_of_shard_id, shard_index_of_target, ip_port_to_delete
):
    requests.put("http://" + ip_port_to_delete + "/reset")
    random_node = choice(members_of_shard_id)
    shards.remove_node(shard_id, random_node)
    shards.add_node(shard_index_of_target, random_node)
    shards.remove_node(shard_index_of_target, ip_port_to_delete)


def broadcast_unable_to_access(shards, dead_shard):
    # set other shards to show "Unable to access key: <key>"
    # for shard_id, shard_members in shards.get_directory.items():
    #     if shard_id != dead_shard:
    pass


def reconstruct_shard(shards, index_to_delete, ip_port_to_delete):
    shard_directory = shards.get_directory()
    shard_index_of_target = index_to_delete % shards.get_shard_size()
    shard_members_of_target = shards.get_members_in_ID(shard_index_of_target)

    for shard_id, nodes in shard_directory.items():
        members_of_shard_id = shards.get_members_in_ID(shard_id)

        shard_id_not_equal_to_target_shard = shard_id != shard_index_of_target
        current_shard_greater_than_target_shard = (
            len(members_of_shard_id) == len(shard_members_of_target) + 1
        )

        if (
            shard_id_not_equal_to_target_shard
            and current_shard_greater_than_target_shard
        ):
            exchange_shards(
                shards,
                shard_id,
                members_of_shard_id,
                shard_index_of_target,
                ip_port_to_delete,
            )

    target_still_in_target_shard = ip_port_to_delete in shards.get_members_in_ID(
        shard_index_of_target
    )

    if target_still_in_target_shard:
        shards.remove_node(shard_index_of_target, ip_port_to_delete)
        length_of_target_shard = len(shards.get_members_in_ID(shard_index_of_target))
        if length_of_target_shard == 0:
            broadcast_unable_to_access(shards)
        elif length_of_target_shard == 1:
            shards.change_shard_size_superficial(shards.get_shard_size() - 1)


def broadcast(ip_port_to_delete, ips):
    payload_to_send = {"ip_port": ip_port_to_delete, "checkpoint": True}
    my_ip = environ.get("IP_PORT")
    for ip in ips:
        if ip == my_ip:
            continue
        url = "http://" + ip + "/view"
        requests.delete(url, data=payload_to_send)


# update Shards directory by calling shards.update_view()
def delete_handling(request, details):
    clock = details["clock"]
    shards = details["shards"]

    body_unicode = request.body.decode("utf-8")
    body = urllib.parse.parse_qs(body_unicode)
    ip_port_to_delete = body["ip_port"][0]
    checkpoint = None
    if "checkpoint" in body:
        checkpoint = body["checkpoint"][0]

    result_msg = ""
    msg = ""
    statuscode = 200
    number_of_shards = environ.get("S")
    ips = get_array_views()
    response_content = {
        "result": "Success",
        "msg": "Successfully removed %s from view" % ip_port_to_delete,
    }

    if ip_port_to_delete in ips:
        index_to_delete = get_index_of_target_in_views(ip_port_to_delete)

        delete_ip(clock, ip_port_to_delete, ips)

        reconstruct_shard(shards, index_to_delete, ip_port_to_delete)

        if checkpoint is None:
            broadcast(ip_port_to_delete, ips)

    else:
        response_content = {
            "result": "Error",
            "msg": ip_port_to_delete + " is not in current view",
        }
        statuscode = 404

    return JsonResponse(response_content, status=statuscode)
