import requests

url = "http://10.232.0.10:8000/login"

payload = {'username=oct1003&password=xbh914&accesscode1=DISABLE&anonymous=DISABLE&checkbox=on&checkbox1=on': ''}

class AutoReconnectService:
    def __init__(self):
        pass

    @staticmethod
    async def login():
        response = requests.request("POST", url, data=payload, verify=False)

        if response.status == 200:
            print("succesfully logged in")
        else:
            print("failed to login, status code: ", res.status)
