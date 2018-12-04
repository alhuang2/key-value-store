# Actual logic for PUT/DELETE function for leader
from django.http import JsonResponse
from os import environ
from hashlib import sha1
import urllib.parse
import requests


def put_handling(request, details):
    clock = details['clock']
    shards = details['shards']
    resultmsg = ""
    msg = ""
    statuscode = 200
    body = request.body.decode('utf-8')

    new_ip_port = body.split('=')[1]
    new_ip_port = urllib.parse.unquote_plus(new_ip_port)

    all_ips = urllib.parse.unquote_plus(environ.get("VIEW"))
    for curr_ip_port in all_ips.split(","):
        # print("testddd")
        if curr_ip_port != new_ip_port:
            # print("http://"+new_ip_port+"/add-view")
            requests.put("http://"+new_ip_port+"/add-view",
                         data={'view': environ.get("VIEW")})
            break

    if new_ip_port not in environ["VIEW"]:
        environ["VIEW"] = environ["VIEW"] + "," + new_ip_port
        shards.update_view()

        all_ips = urllib.parse.unquote_plus(environ.get("VIEW"))

        # inefficient broadcast. change later
        for curr_ip_port in all_ips.split(","):
            current_ip_is_not_new_ip = (curr_ip_port != new_ip_port)
            current_ip_is_not_client_ip = (
                curr_ip_port != environ.get("IP_PORT"))
            if current_ip_is_not_new_ip and current_ip_is_not_client_ip:
                requests.put("http://"+curr_ip_port+"/view",
                             data={'ip_port': new_ip_port})
        clock.push()
        resultmsg = "Success"
        msg = "Successfully added " + new_ip_port + " to view"
        statuscode = 200

    else:
        resultmsg = "Error"
        msg = new_ip_port + " is already in view"
        statuscode = 400

    return JsonResponse({"result": resultmsg, "msg": msg}, status=statuscode)
