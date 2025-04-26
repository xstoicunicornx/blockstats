import json
import requests

RPC_USER = '__cookie__'
RPC_PASSWORD = 'set your own password or look at the contents of the .cookie file'
RPC_URL = f'http://127.0.0.1:8332/'

HEADERS = {'content-type': 'application/json'}

def rpc_call(method, params=None):
    payload = json.dumps({
        "method": method,
        "params": params or [],
        "jsonrpc": "2.0",
        "id": 0,
    })
    response = requests.post(RPC_URL, headers=HEADERS, data=payload, auth=(RPC_USER, RPC_PASSWORD))
    response.raise_for_status()
    return response.json()['result']
