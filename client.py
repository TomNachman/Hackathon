import select
import socket
import sys
import threading
import time
from socket import *
import struct
import config


def validate_header_data(decode_data) -> bool:
    """
    Validates that the sent data contains the MAGIC_COOKIE ,M_TYPE
    @param decode_data: Received data to check.
    @return: True if data is valid, else False.
    """
    return len(decode_data) != 3 or decode_data[0] != config.MAGIC_COOKIE or decode_data[1] != config.MESSAGE_TYPE


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
        self.magic_cookie = config.MAGIC_COOKIE
        self.offer_message = config.MESSAGE_TYPE
        # Sockets init
        self.tcp_socket = None
        self.udp_sock = socket(AF_INET, SOCK_DGRAM)
        self.udp_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.udp_sock.bind((config.UDP_IP, config.UDP_PORT))
        self.game_over = True  # Variable providing info whether to keep sending messages or not.

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
                if validate_header_data(decode_data):
                    self.connect_to_server(server_ip=address[0], server_tcp_port=decode_data[2])
                    # in case we 'break' means established succeed !
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

    def messages_from_server(self) -> bool:
        while True:
            try:
                message = self.tcp_socket.recv(config.BUFFER_SIZE).decode('utf-8')
                if len(message) > 0:
                    print(f'{config.OK_BLUE}{message}{config.END}')

                if message.startswith('Game over!') or not message:
                    self.game_over = True
                    print(f'{config.WARNING}Server disconnected, listening for offer requests...{config.END}')
                    return False
                # First message, client is waiting for it after the tcp connection.
                if message.startswith('Welcome'):
                    return True

            except KeyboardInterrupt as e:
                # Would be handled on main() function.
                raise e

            except:
                raise ConnectionRefusedError("Server is down.")


    def run_game(self):
        """
        This function initiate the game
        """
        while True:
            time.sleep(1)
            try:
                self.listen_state()  # searching for server and connecting over TCP
                start_game = client.messages_from_server()  # waits for game initiating  by server
                if start_game:
                    client.game_over = False
                    messages_thread = threading.Thread(target=client.messages_from_server)
                    # listening for tcp messages in the background
                    messages_thread.start()
                    # TODO : handle keyboard here
                    # waits for a thread to die
                    messages_thread.join()

                # close tcp connection
                client.tcp_socket.shutdown(socket.SHUT_RDWR)
                client.tcp_socket.close()

            except ConnectionRefusedError:
                print('Server disconnected')

            except:
                print('Error, reconnecting...')
                continue


if __name__ == "__main__":
    client = Client('NSO')
    print(f"{config.OK_GREEN}Client started, listening for offer requests...{config.END}")
    try:
        client.run_game()
    except KeyboardInterrupt:
        print('KeyboardInterrupt')
        pass
    print("Client Done!")
