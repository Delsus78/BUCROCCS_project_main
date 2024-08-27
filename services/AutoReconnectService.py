import asyncio

import requests

url = "http://10.232.0.10:8000/login"

payload = {
    'username': 'oct1003',
    'password': 'xbh914',
    'accesscode1': 'DISABLE',
    'anonymous': 'DISABLE',
    'checkbox': 'on',
    'checkbox1': 'on'
}

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Connection': 'keep-alive',
    'Origin': 'http://10.232.0.10:8000',
    'Referer': 'http://10.232.0.10:8000/login.html',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
}


class AutoReconnectService:
    def __init__(self, controller):
        self.controller = controller

    async def login(self):
        while True:
            try:
                response = requests.post(url, data=payload, headers=headers, verify=False, timeout=5)

                if response.status_code == 200:
                    print("Successfully logged in")
                    return

                raise Exception("Failed to login, status code:", response.status_code)

            except Exception as e:
                print("An error occurred:", e)
            await asyncio.sleep(3)
