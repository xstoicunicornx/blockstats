import json
import requests

RPC_USER = '__cookie__'
RPC_COOKIE_FILE_PATH = '/data/bitcoin/.cookie'
RPC_URL = f'http://127.0.0.1:8332/'

HEADERS = {'content-type': 'application/json'}

with open(RPC_COOKIE_FILE_PATH, 'r') as file:
    cookie = file.read().rstrip().replace(RPC_USER + ':', '')

def rpc_call(method, params=None):
    payload = json.dumps({
        "method": method,
        "params": params or [],
        "jsonrpc": "2.0",
        "id": 0,
    })
    response = requests.post(RPC_URL, headers=HEADERS, data=payload, auth=(RPC_USER, cookie))
    response.raise_for_status()
    return response.json()['result']
