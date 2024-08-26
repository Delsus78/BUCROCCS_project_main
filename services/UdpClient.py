import json
import socket
import asyncio


class UdpClient:
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.loop = asyncio.get_event_loop()
        self.init_socket()
        self.lock = asyncio.Lock()  # Create a lock

    def init_socket(self):
        try:
            self.sock.close()
        except Exception:
            pass
        finally:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.setblocking(False)

    async def retrieve_data(self, command, id_str, json_data=None, view=None):
        async with self.lock:
            while True:
                try:
                    # sending
                    message = f"{command},{id_str}"
                    if json_data:
                        message += f",{json.dumps(json_data)}"

                    if view:
                        view.send_message_to_udpserver(message)

                    self.sock.sendto(message.encode('utf-8'), (self.server_ip, self.server_port))
                    break
                except Exception as e:
                    print(f"[ERROR] Error while sending data to server: {e}")
                    self.init_socket()

            # retrieve data
            max_try = 20
            timeout = 5  # seconds
            while max_try > 0:
                try:
                    data = await asyncio.wait_for(self.loop.sock_recv(self.sock, 2048), timeout)
                    data_str = data.decode('utf-8')

                    if view:
                        view.receive_message_from_udpserver(data_str)

                    return await self.checking_data(data_str, command, id_str)
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

    @staticmethod
    async def checking_data(data_str, command, id_str):
        resulted_json = {}
        if 'No' in data_str:
            return {}

        if 'saved' in data_str:
            print(f'[SAVED] Data saved correctly using command : {command}, {id_str} ')
            return {}

        try:
            resulted_json = json.loads(data_str)
        except json.JSONDecodeError as e:
            print('Error while decoding json data : ', data_str, 'is not a valid json',
                  'command:', command, 'id:', id_str, e.msg)
        finally:
            return resulted_json
