import urllib.parse
import requests
import json
from django.conf import settings


def encode_name(raw_name):
    return urllib.parse.quote(raw_name, safe='') \
        .replace('.', '%2e') \
        .replace('-', '%2d') \
        .replace('~', '%7e') \
        .replace('_', '%5f') \
        .replace('%', '-')


def user_exists(user):
    user = encode_name(str(user))
    response = requests.get(f'{settings.BASE_HUB_URL}/hub/api/users/{user}',
                             headers={'Authorization': f'token {settings.HUB_TOKEN}'})
    return response.status_code == 200


def create_user(user):
    user = encode_name(str(user))
    response = requests.post(f'{settings.BASE_HUB_URL}/hub/api/users/{user}',
                             headers={'Authorization': f'token {settings.HUB_TOKEN}'})
    if response.status_code == 201 or response.status_code == 200: return True
    else: raise RuntimeError(response.text)


def spawn_server(user, server_name, image):
    user = encode_name(str(user))
    # server_name = encode_name(str(server_name))
    response = requests.post(f'{settings.BASE_HUB_URL}/hub/api/users/{user}/servers/{server_name}',
                             headers={'Authorization': f'token {settings.HUB_TOKEN}'},
                             data=json.dumps({'image': image}))

    if response.status_code == 201 or response.status_code == 200: return True
    elif response.status_code == 400 and 'already running' in response.text: return True
    else: raise RuntimeError(response.text)


def stop_server(user, server_name, remove_server=False):
    user = encode_name(str(user))
    # server_name = encode_name(str(server_name))
    response = requests.delete(f'{settings.BASE_HUB_URL}/hub/api/users/{user}/servers/{server_name}',
                             headers={'Authorization': f'token {settings.HUB_TOKEN}'},
                             data=json.dumps({"remove": remove_server}))

    if response.status_code == 204 or response.status_code == 200: return True
    else: raise RuntimeError(response.text)


def delete_server(user, server_name):
    try:
        stop_server(user, server_name, remove_server=True)
    except RuntimeError as response:
        if '404' in repr(response): pass
        else: raise response
