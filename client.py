from my_socket import Socket
from datetime import datetime

from os import system
import asyncio


class Client(Socket):
    def __init__(self):
        super(Client, self).__init__()
        self.messages = ""

    def set_up(self):
        try:
            self.socket.connect(("0.0.0.0", 1234))
        except ConnectionRefusedError:
            print("Sorry, server is offline")
            exit(0)
        self.socket.setblocking(False)

    async def listen_socket(self, listened_socket=None):
        while True:
            data = await self.main_loop.sock_recv(self.socket, 1024)
            self.messages += f"{datetime.now().date()}: {data.decode()}\n"

            system("clear")
            print(self.messages)

    async def send_data(self, data=None):
        while True:
            data = await self.main_loop.run_in_executor(None, input)
            await self.main_loop.sock_sendall(self.socket, data.encode())

    async def main(self):
        await asyncio.gather(
            self.main_loop.create_task(self.listen_socket()),
            self.main_loop.create_task(self.send_data()),
        )

if __name__ == '__main__':
    client = Client()
    client.set_up()
    client.start()