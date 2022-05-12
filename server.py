import asyncio
import socket
from loguru import logger
from my_socket import Socket

logger.add("debug.log", format="{time} {level} {message}", level="DEBUG", rotation="10 KB")


class Server(Socket):
    def __init__(self):
        super(Server, self).__init__()
        self.users = []

    def set_up(self):
        self.socket.bind(("0.0.0.0", 1234))
        self.socket.listen(5)
        self.socket.setblocking(False)
        logger.debug("Server listening (debug)")

    async def send_data(self, data=None):
        for user in self.users:
            await self.main_loop.sock_sendall(user, data)

    async def listen_socket(self, listened_socket=None):
        if not listened_socket:
            return
        while True:
            try:
                data = await self.main_loop.sock_recv(listened_socket, 1024)
                x = self.request_processing(data.decode())

                self.send_data_for_approval(x)
                # conn = socket.create_connection(('vragi-vezde.to.digital', 51624))
                # conn.send(f"АМОЖНА? РКСОК/1.0\r\n{x}".encode())

                await self.send_data(x)
            except ConnectionResetError:
                print("Client removed...")
                self.users.remove(listened_socket)
                return

    async def accept_sockets(self):
        while True:
            user_socket, address = await self.main_loop.sock_accept(self.socket)
            logger.debug(f"User <{address[0]}> connected!> (debug)")

            self.users.append(user_socket)
            self.main_loop.create_task(self.listen_socket(user_socket))

    async def main(self):
        await self.main_loop.create_task(self.accept_sockets())

    def request_processing(self, raw_data):
        if str(raw_data).endswith('\r\n\r\n'):
            data_as_list = raw_data.split()
            if not self.requests_correctness_checking(data_as_list):
                respond = 'НИПОНЯЛ РКСОК/1.0\r\n\r\n'.encode()
            else:
                respond = raw_data.encode()
        else:
            respond = 'НИПОНЯЛ РКСОК/1.0\r\n\r\n'.encode()
        return respond

    def requests_correctness_checking(self, request: list) -> bool:
        """Check if request received from client is correct"""
        if 'РКСОК/1.0' in request and request[0] in ('ОТДОВАЙ', 'УДОЛИ', 'ЗОПИШИ', 'АМОЖНА'):
            last_name_word_index = request.index('РКСОК/1.0')
            name = ' '.join(request[1:last_name_word_index])
            if len(name) <= 30:
                return True
        return False

    def send_data_for_approval(self, data):
        conn = socket.create_connection(('vragi-vezde.to.digital', 51624))
        conn.send(f"АМОЖНА? РКСОК/1.0\r\n{data}".encode())

if __name__ == '__main__':
    server = Server()
    server.set_up()
    server.start()
