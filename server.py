import config
import socket
from scapy.arch import get_if_addr
import time
import threading


class Server:
    def __init__(self):
        # Server Global Parameters
        self.network_ip = get_if_addr('eth1')
        self.udp_dest_port = config.UDP_PORT

        self.sending_udp_messages = False  # Tells the TCP conn when to stop accepting clients.
        self.receive_m = False
        self.master_tcp_socket = None
        self.udp_socket = None
        self.game_mode = False

    def init_sockets(self) -> None:
        """
            This function initiates UDP and TCP scokets ,
            binds the udp_socket to our port and Enable broadcasting mode,
            binds the master_tcp_socket to out port(2016)

        """
        # initializing UDP socket
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        # initializing TCP master socket
        self.master_tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.master_tcp_socket.settimeout(0.1)
        self.master_tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.master_tcp_socket.bind((self.network_ip, config.TCP_PORT))
        self.master_tcp_socket.listen(1)

    def start_server(self):
        """
        This function activate ports tcp & udp (happens once!!!)
        """
        try:
            self.init_sockets()
            print("Server started, listening on IP address {}".format(self.network_ip))
            time.sleep(1.5)
        except OSError:
            time.sleep(1)
        finally:
            self.server_state_tcp_listening()

if __name__ == "__main__":
    server = Server()
    server.start_server()
