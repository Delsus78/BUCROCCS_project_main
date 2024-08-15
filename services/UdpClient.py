import json
import socket
import asyncio


class UdpClient:
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.loop = asyncio.get_event_loop()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setblocking(False)  # Make the socket non-blocking
        self.lock = asyncio.Lock()  # Create a lock

    async def retrieve_data(self, command, id_str, json_data=None, view=None):
        async with self.lock:

            # sending
            message = f"{command},{id_str}"
            if json_data:
                message += f",{json.dumps(json_data)}"

            if view:
                view.send_message_to_udpserver(message)

            self.sock.sendto(message.encode('utf-8'), (self.server_ip, self.server_port))

            # retrieve data
            max_try = 20
            timeout = 5  # seconds
            while max_try > 0:
                try:
                    data = await asyncio.wait_for(self.loop.sock_recv(self.sock, 2048), timeout)
                    dataStr = data.decode('utf-8')

                    if view:
                        view.receive_message_from_udpserver(dataStr)

                    return await self.checking_data(dataStr, command, id_str)
                except asyncio.TimeoutError:
                    print("[ERROR] Timeout while waiting for data from server.")
                    break
                except BlockingIOError:
                    max_try -= 1
                    print(f"[WARNING] Retrying to get data from udp server, {max_try} tries left.")
                    await asyncio.sleep(0.1)  # Avoid busy-waiting
            print("[ERROR] Failed to retrieve data after multiple attempts.")
            return {'Error': True}

    def close(self):
        self.sock.close()

    async def checking_data(self, dataStr, command, id_str):
        resultedJson = {}
        if 'No' in dataStr:
            return {}

        if 'saved' in dataStr:
            print(f'[SAVED] Data saved correctly using command : {command}, {id_str} ')
            return {}

        try:
            resultedJson = json.loads(dataStr)
        except json.JSONDecodeError as e:
            print('Error while decoding json data : ', dataStr, 'is not a valid json',
                  'command:', command, 'id:', id_str, e.msg)
        finally:
            return resultedJson
