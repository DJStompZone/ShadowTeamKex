from abc import ABC, abstractmethod
import socket
import threading
import logging

from shadowteamkex.kex import KeyExchangeHandler, dh

class TCPRole(ABC):
    @abstractmethod
    def run(self):
        pass

class ListenerRole(TCPRole):
    def __init__(self, parameters: dh.DHParameters, peer_port: int, key_exchange_handler: KeyExchangeHandler):
        self.parameters = parameters
        self.peer_port = peer_port
        self.key_exchange_handler = key_exchange_handler

    def listen_on_port(self):
        logging.debug(f"Listening on port {self.peer_port}")
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('0.0.0.0', self.peer_port))
        server_socket.listen(1)
        logging.debug(f"Server listening on port {self.peer_port}")

        while True:
            conn, addr = server_socket.accept()
            logging.info(f"Connection from {addr} on port {self.peer_port}")
            self.key_exchange_handler.perform_dh_exchange(conn, self.parameters)

    def run(self):
        logging.debug("Starting listener role")
        threading.Thread(target=self.listen_on_port).start()

class InitiatorRole(TCPRole):
    def __init__(self, peer_ip: str, parameters: dh.DHParameters, peer_port: int, key_exchange_handler: KeyExchangeHandler):
        self.peer_ip = peer_ip
        self.parameters = parameters
        self.peer_port = peer_port
        self.key_exchange_handler = key_exchange_handler

    def run(self):
        logging.debug(f"Starting client to connect to {self.peer_ip}:{self.peer_port}")
        while True:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((self.peer_ip, self.peer_port))
                self.key_exchange_handler.perform_dh_exchange(sock, self.parameters)
                break
            except Exception as e:
                logging.warning(f"Failed to connect on port {self.peer_port}: {e}")
                sock.close()
