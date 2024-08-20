import http.client
from codecs import encode

conn = http.client.HTTPSConnection("10.232.0.10", 8000)
dataList = []
boundary = 'wL36Yn8afVp8Ag7AmP8qZ0SA4n1v9T'
dataList.append(encode('--' + boundary))
dataList.append(encode(
    'Content-Disposition: form-data; name=username=oct1003&password=xbh914&accesscode1=DISABLE&anonymous=DISABLE&checkbox=on&checkbox1=on;'))

dataList.append(encode('Content-Type: {}'.format('text/plain')))
dataList.append(encode(''))

dataList.append(encode(""))
dataList.append(encode('--' + boundary + '--'))
dataList.append(encode(''))
body = b'\r\n'.join(dataList)
payload = body
headers = {
    'Content-type': 'multipart/form-data; boundary={}'.format(boundary)
}


class AutoReconnectService:
    def __init__(self):
        pass

    @staticmethod
    async def login():
        conn.request("POST", "/login", payload, headers)
        res = conn.getresponse()

        if res.status == 200:
            print("succesfully logged in")
        else:
            print("failed to login, status code: ", res.status)
