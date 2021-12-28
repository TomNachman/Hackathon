import struct
import config
import socket
from scapy.arch import get_if_addr
import time
import threading


def create_game_start_message(players: list) -> str:
    """
    Creates a start game message with the teams' names.
    :param players: list of pplayers
    :return staring message
    """
    msg = f'{config.OK_CYAN}Welcome to Quick Maths.{config.END}'
    for i, p in enumerate(players, 1):
        msg += '\nPlayer ' + str(i) + ': ' + p[2]
    msg += '==\n'
    msg += 'Please answer the following question as fast as you can:\n'
    return msg


class Server:
    def __init__(self):
        # Server Global Parameters
        self.network_ip = get_if_addr('eth1')  # dev network (eth1, 172.1.0/24)
        self.udp_dest_port = config.UDP_PORT
        self.sending_udp_messages = False  # Tells the TCP conn when to stop accepting clients.
        self.receive_messages = False  # boolean var that indicates that the server is receiving messages
        self.master_tcp_socket = None
        self.udp_socket = None
        self.game_mode = False
        self.searching_for_players = True
        self.client_list = []
        self.winner = None
        self.math_answer = None

    def init_sockets(self) -> None:
        """
            This function initiates UDP and TCP sockets ,
            binds the udp_socket to our port and Enable broadcasting mode,
            binds the master_tcp_socket to out port(2016)

        """
        # initializing UDP socket
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        # initializing TCP master socket
        self.master_tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.master_tcp_socket.settimeout(1)  # timeout for listening
        self.master_tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.master_tcp_socket.bind((self.network_ip, config.TCP_PORT))
        self.master_tcp_socket.listen(1)  # Enable a server to accept connections

    def waiting_for_clients_state(self) -> None:
        try:
            while True:
                # A sleep so that loop wouldn't run forever.
                print('Waiting 2 seconds')
                time.sleep(2)
                # Thread initiation to send udp message on broadcast, we set daemon because we don't need a guarantee
                # that broadcast_udp/accept_connections function we get executed completely
                udp_broadcast_thread = threading.Thread(target=server.broadcast_udp, daemon=True)
                udp_broadcast_thread.start()
                # Thread initiation to receive tcp connections.
                tcp_receive_thread = threading.Thread(target=server.accept_connections, daemon=True)
                tcp_receive_thread.start()

                udp_broadcast_thread.join()
                tcp_receive_thread.join()

                if len(server.client_list) < 2:
                    print(f"{config.WARNING}Not enough players! Restarting...{config.END}")
                    continue

                start_msg = create_game_start_message(self.client_list)
                question, answer = config.generate_simple_math()
                self.math_answer = answer
                self.send_message_to_clients(start_msg + question)
                # Thread initiation to start listening for client's messages.
                x = threading.Thread(target=server.get_messages_from_clients)
                x.start()
                x.join()
                self.send_finish_message()
                self.release_clients_and_reset()


        except:
            pass

    def broadcast_udp(self) -> None:
        """
        This function broadcast offer request every second for 10 seconds over a UDP connection
        """

        message_to_send = struct.pack('IbH', config.MAGIC_COOKIE, config.MESSAGE_TYPE, config.TCP_PORT)
        self.searching_for_players = True
        for i in range(5):
            if len(self.client_list) < 2:
                print(f'{config.BOLD}sending udp message number {i}...{config.END}')
                self.udp_socket.sendto(message_to_send, (config.UDP_IP, config.UDP_PORT))
                time.sleep(1)
        self.searching_for_players = False

    def accept_connections(self) -> None:
        """
        Accepts TCP connection requests from clients on parallel to sending offers.
        """
        while self.searching_for_players:
            try:
                sock, addr = self.master_tcp_socket.accept()
                if sock and len(server.client_list) <= 2:
                    team_name = str(sock.recv(config.BUFFER_SIZE).decode('utf-8'))
                    self.client_list.append((sock, addr, team_name))
            except socket.timeout:
                continue

    def get_messages_from_clients(self) -> None:
        """
        Opens a thread for each client so the server can recieve incoming messages from all clients simultanously
        """
        self.receive_messages = True
        for client in self.client_list:
            threading.Thread(target=self.get_message, args=(client,)).start()
        print('listening for 10 sec for each client')
        start = time.time()
        while time.time() - start < 10 and self.receive_messages:
            time.sleep(1)

    def get_message(self, client: tuple):
        """
        Recieves a message from a single client.
        @param sock: Socket of the client.
        """
        while self.receive_messages:
            m = client[0].recv(config.BUFFER_SIZE).decode('utf-8')
            if m and str(m) == str(self.math_answer):
                self.winner = client[2]
                self.receive_messages = False
            elif m:
                # in case client is wrong the other client
                self.winner = self.client_list[1][2] if self.client_list[0][2] == client[2] else self.client_list[0][2]
                self.receive_messages = False

    def send_message_to_clients(self, message: str) -> None:
        """
        Sends message to all clients over tcp.
        @param message: String to send
        """
        for client in self.client_list:
            client[0].send(bytes(message, 'utf-8'))

    def release_clients_and_reset(self):
        """
        Closes connection to all clients in the end of a game.
        """
        for client in self.client_list:
            try:
                client[0].close()
            except:
                continue

        # reset class params
        self.client_list = []
        self.sending_udp_messages = False
        self.receive_messages = False
        self.game_mode = False
        self.searching_for_players = True
        self.math_answer = None
        self.winner = None

    def start_server(self):
        """
        This function starts the server
        """
        try:
            self.init_sockets()
            print("Server started, listening on IP address {}".format(self.network_ip))
            time.sleep(1.5)
        except OSError:
            time.sleep(1)
        finally:
            self.waiting_for_clients_state()

    def send_finish_message(self):
        self.send_message_to_clients(f'{config.RED}Game over!{config.END}\n')
        print(self.math_answer)
        self.send_message_to_clients(
            f'{config.BOLD}The correct answer was {config.UNDERLINE}{str(self.math_answer)}{config.END}!\n')
        if self.winner:
            self.send_message_to_clients(
                f'Congratulations to the winner: {config.BG_GREEN}{self.winner}{config.END}\n')
        else:
            self.send_message_to_clients(f'It`s a {config.BOLD}DRAW{config.END}\n')


if __name__ == "__main__":
    server = Server()
    server.start_server()

