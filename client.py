import select
import socket
import sys
import time
from socket import *
import struct
import config


def validate_data(decode_data) -> bool:
    """
    Validates that the sent data contains the MAGIC_COOKIE and M_TYPE
    @param decode_data: Received data to check.
    @return: True if data is valid, else False.
    """
    return len(decode_data) == 3 and decode_data[0] == config.MAGIC_COOKIE and decode_data[1] == config.MESSAGE_TYPE


class Client:
    def __init__(self, group_name: str):
        """
        constructor to a client
        group_name - should be a funny name.
        tcp_socket - a future variable holds the socket of the game.
        magic_cookie,offer_message - variable that holds hackathon protocol values.
        game_running - boolean that express the status of the game.
        """
        self.group_name = group_name
        # Sockets init
        self.tcp_socket = None
        self.udp_sock = socket(AF_INET, SOCK_DGRAM)
        self.udp_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.udp_sock.bind((config.UDP_IP, config.UDP_PORT))
        self.game_running = True  # Variable providing info whether to keep sending messages or not.

    def listen_state(self) -> None:
        """
        Client listening on UDP port until he receives a connection offers from server (listens on UDP).
        Receives invitation request message, validates the data that has been sent.
        @return: decoded data - tuple of server data and server address.
        """
        while True:
            encode_data, address = self.udp_sock.recvfrom(
                config.BUFFER_SIZE)  # The number of bytes to be read from the UDP socket(1024)
            print(f"received offer from {address[0]}, attempting to connect...")

            try:
                decode_data = struct.unpack('IbH', encode_data)
                if validate_data(decode_data):
                    self.connect_to_server(server_ip=address[0], server_tcp_port=decode_data[2])
                    # if we break that means that connecto to server succesded
                    break
            except:
                # Continue looking for connections if data is invalid.
                print('Data is invalid.')
                continue

    def connect_to_server(self, server_ip, server_tcp_port) -> None:
        """
        Initiates a new tcp socket connections.
        As soon as client is connected to a server, the client sends his name(TEAM NAME) to the server.
        @param server_ip: IP address of the server.
        @param server_tcp_port: Server's port.
        """
        try:
            self.tcp_socket = socket(AF_INET, SOCK_STREAM)
            self.tcp_socket.connect((server_ip, server_tcp_port))
            self.tcp_socket.send(bytes(self.group_name + '\n', 'utf-8'))

        except:
            print("TCP initiation went wrong.")

    def message_from_server_handler(self, msg) -> None:
        print(msg.decode("utf-8"))
        if not self.game_running:
            self.game_running = True
            return
        if self.game_running:
            self.game_running = False

    def run_game(self):
        """
        This function initiate the game
        """
        while True:
            time.sleep(0.1)
            try:
                self.listen_state()  # searching for server and connecting over TCP
                welcome_msg = self.tcp_socket.recv(config.BUFFER_SIZE).decode('utf-8')
                print(f'{config.OK_BLUE}{welcome_msg}{config.END}')

                # set the socket to be non blocking in order to be able to read and write simultaneously
                self.tcp_socket.setblocking(False)
                while self.game_running:
                    time.sleep(0.1)
                    # Wait for some kind of I/O operation
                    data = select.select([sys.stdin], [], [], 0)
                    if data[0] and self.game_running:
                        char_to_send = sys.stdin.read(1)
                        self.tcp_socket.send(bytes(char_to_send, 'utf-8'))
                    try:
                        msg_from_server = self.tcp_socket.recv(config.BUFFER_SIZE)
                        self.message_from_server_handler(msg_from_server)
                        if not self.game_running or msg_from_server:
                            break
                    except:
                        pass
                # close tcp connection
                client.tcp_socket.close()

            except ConnectionRefusedError:
                print('Server disconnected')

            except Exception as e:
                print('Error, reconnecting...')
                continue


if __name__ == "__main__":
    client = Client('Stuxnet')
    print(f"{config.OK_GREEN}Client started, listening for offer requests...{config.END}")
    try:
        client.run_game()
    except KeyboardInterrupt:
        print('KeyboardInterrupt')
        pass
    print("Client Done!")
