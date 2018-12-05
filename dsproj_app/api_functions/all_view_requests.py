from django.http import JsonResponse
import requests
import json
from os import environ
from django.conf import settings
import urllib.parse


def view_request(request, clock):
    if (request.method == 'GET'):
        view_string = environ.get("VIEW")
        return JsonResponse({"view": view_string}, status=200)

    elif (request.method == 'PUT'):
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

    elif(request.method == 'DELETE'):
        result_msg = ""
        msg = ""
        statuscode = 200

        def delete_ip(request_body, ip_port_to_delete):
            # print("@@@ " + ip_port_to_delete)

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

        ip_port_to_delete = get_ip(request.body)

        result_msg = "Success"
        msg = "Successfully removed %s from view" % ip_port_to_delete

        all_ips = urllib.parse.unquote_plus(environ.get("VIEW"))

        # inefficient broadcast. change later
        is_exists = delete_ip(request.body, ip_port_to_delete)
        # print('&&&&&&& ', is_exists)
        if is_exists:
            ips = all_ips.split(",")
            if ip_port_to_delete == environ.get("IP_PORT"):
                environ["VIEW"] = ip_port_to_delete
            for curr_ip_port in ips:
                current_ip_is_not_client_ip = (
                    curr_ip_port != environ.get("IP_PORT"))
                if current_ip_is_not_client_ip:
                    # set VIEW of deleted view to itself only
                    requests.delete("http://"+curr_ip_port+"/view",
                                    data={'ip_port': ip_port_to_delete})

        else:
            result_msg = "Error"
            msg = ip_port_to_delete + " is not in current view"
            statuscode = 404

        return JsonResponse({"result": result_msg, "msg": msg}, status=statuscode)
