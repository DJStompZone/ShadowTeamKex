import threading
import socket
import random
import time
import logging
import uuid
from typing import Optional, Tuple

class PreconnectHandler:
    PORT_RANGE = [17377]

    def __init__(self, peer_ip: str):
        self.peer_ip = peer_ip
        self.session_id = str(uuid.uuid4())
        self.random_value = random.randint(0, 1000000)
        self.timestamp = time.time()
        self.selected_port = random.choice(self.PORT_RANGE)
        self.handshake_event = threading.Event()

    def create_preconnect_socket(self, socket_port: int = 17377) -> socket.socket:
        logging.debug(f"Creating UDP socket on port {socket_port}")
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        udp_socket.bind(('', socket_port))
        udp_socket.settimeout(20)
        logging.debug("UDP socket created and configured")
        return udp_socket

    def send_negotiation_packet(self, udp_socket: socket.socket):
        message = f"{self.random_value},{self.timestamp},{self.session_id},{self.selected_port}".encode('utf-8')
        logging.debug(f"Sending negotiation packet: {message}")
        udp_socket.sendto(message, (self.peer_ip, 17377))

    def receive_negotiation_packet(self, udp_socket: socket.socket) -> Tuple[int, float, str, int]:
        logging.debug("Listening for negotiation packet")
        while True:
            peer_message, _ = udp_socket.recvfrom(1024)
            peer_random_value, peer_timestamp, peer_session_id, peer_port = peer_message.decode('utf-8').split(',')
            if peer_session_id != self.session_id:
                logging.debug(f"Received negotiation packet: {peer_message}")
                return int(peer_random_value), float(peer_timestamp), peer_session_id, int(peer_port)
            logging.debug("Ignored own negotiation packet")

    def send_handshake_packet(self, udp_socket: socket.socket):
        message = f"HANDSHAKE,{self.session_id}".encode('utf-8')
        logging.debug(f"Sending handshake packet: {message}")
        for _ in range(3):
            udp_socket.sendto(message, (self.peer_ip, 17378))

    def receive_handshake_packet(self, udp_socket: socket.socket):
        logging.debug("Listening for handshake packet")
        while not self.handshake_event.is_set():
            try:
                peer_message, _ = udp_socket.recvfrom(1024)
                message, peer_session_id = peer_message.decode('utf-8').split(',')
                if message == "HANDSHAKE" and peer_session_id != self.session_id:
                    logging.debug(f"Received handshake packet: {peer_message}")
                    self.handshake_event.set()
            except socket.timeout:
                continue

    def role_negotiation_attempt(self, udp_socket: socket.socket) -> Optional[Tuple[str, int]]:
        try:
            peer_random_value, peer_timestamp, peer_session_id, peer_port = self.receive_negotiation_packet(udp_socket)
            logging.info(f"Received negotiation packet with random value: {peer_random_value}, timestamp: {peer_timestamp}, session ID: {peer_session_id}, port: {peer_port}")

            if self.session_id != peer_session_id:
                if self.random_value > peer_random_value:
                    logging.info("Local peer is initiator")
                    return 'initiator', peer_port
                elif self.random_value < peer_random_value:
                    logging.info("Local peer is listener")
                    self.send_handshake_packet(udp_socket)
                    return 'listener', peer_port
                else:
                    self.random_value = random.randint(0, 1000000)
                    self.timestamp = time.time()
                    self.send_negotiation_packet(udp_socket)
                    logging.info(f"Resent negotiation packet with new random value: {self.random_value} and timestamp: {self.timestamp}")
                    return
        except socket.timeout:
            logging.warning("Socket timeout while waiting for negotiation packet")
            return

    def negotiate_roles(self, max_attempts: int = 10) -> Optional[Tuple[str, int]]:
        logging.debug(f"Starting role negotiation with peer at {self.peer_ip}")
        udp_socket = self.create_preconnect_socket()
        self.send_negotiation_packet(udp_socket)
        logging.info(f"Sent negotiation packet with random value: {self.random_value}, timestamp: {self.timestamp}, session ID: {self.session_id}, port: {self.selected_port}")

        handshake_socket = self.create_preconnect_socket(17378)
        handshake_thread = threading.Thread(target=self.receive_handshake_packet, args=(handshake_socket,))
        handshake_thread.start()

        attempts = 0
        while attempts < max_attempts:
            logging.debug(f"Attempt {attempts + 1} of {max_attempts} for role negotiation")
            roles = self.role_negotiation_attempt(udp_socket)
            if roles:
                role, peer_port = roles
                logging.info(f"Negotiation successful: role: {role}, peer port: {peer_port}")
                return role, peer_port
            logging.warning("Resent negotiation packet due to timeout")
            attempts += 1

        logging.error("Negotiation failed: maximum attempts reached")
        return
