#!/usr/bin/python3
# encoding: utf8

import aiohttp, asyncio, json, os, time
from pathlib import Path
from datetime import datetime
from aiohttp import ClientTimeout
from getpass import getpass

AUTH_TOKEN_FILE = ".auth-token"
TIMEOUT = ClientTimeout(total=5)

def file_age(filepath):
    return int(time.time() - os.path.getmtime(filepath))

async def get_token(username, password):
    file_location = Path(AUTH_TOKEN_FILE)
    if not file_location.is_file() or file_age(AUTH_TOKEN_FILE) >= 3600:
        url = "https://smartcontrol.eon.de/auth"
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        data = {"username": username, "password": password, "method": "login"}

        async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
            async with session.get(url, headers=headers, json=data, allow_redirects=False) as response:
                data = await response.json()
                return data.get('access_token', None)
    else:
        with open(AUTH_TOKEN_FILE, 'r') as token:
            return token.readline()

async def get_watts(access_token):
    today = datetime.now().strftime("%Y-%m-%d")
    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]
    url = f"https://api.n2g-iona.net/v2/power/{today}T00:00:00.000Z/{now}Z"
    headers = {"Accept": "application/json", "Authorization": f"Bearer {access_token}"}

    async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
        async with session.get(url, headers=headers) as response:
            data = await response.json()
            return data['data']['results'][-1]['power']

async def get_kWh(access_token):
    url = "https://api.n2g-iona.net/v2/meter/info"
    headers = {"Accept": "application/json", "Authorization": f"Bearer {access_token}"}

    async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
        async with session.get(url, headers=headers) as response:
            data = await response.json()
            kWh = int(data['data']['Electricity']['CSD'])
            return round(kWh / 1000)

def write_to_file(token):
    file_location = Path(AUTH_TOKEN_FILE)
    if not file_location.is_file() or file_age(AUTH_TOKEN_FILE) >= 3600:
        with open(AUTH_TOKEN_FILE, "w") as text_file:
            text_file.write(token)

async def main():
    try:
        username = input("Benutzername: ")
        password = getpass("Passwort: ")

        token = await get_token(username, password)
        write_to_file(token)

        watts = await get_watts(token)
        kWh = await get_kWh(token)
        print(watts)
        print(kWh)
    except aiohttp.ClientError as e:
        print("Ein Fehler ist aufgetreten:", str(e))

if __name__ == '__main__':
    asyncio.run(main())
