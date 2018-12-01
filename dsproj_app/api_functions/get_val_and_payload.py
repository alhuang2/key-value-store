from urllib.parse import parse_qs
from json import loads

def val_and_payload(request_body):
    body_unicode = request_body.decode('utf-8')
    body = (parse_qs(body_unicode))

    payload_json = loads(body['payload'][0])
    if 'val' in body:
        val = body['val'][0]
    else:
        val = None

    val_payload = {
        "val": val,
        "payload_json": payload_json
    }
    return val_payload

    # payload_json = {"vc": [0,0,0], "pos", 1}
