from django.http import JsonResponse
from os import environ
from dsproj_app.views import get_array_views
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

    # check if removing node will still hold n > 2*S
    if (len(all_ips) - 1 > 2*number_of_shards):
        print("cool, proceed")
    else:

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
