import socket
import logging
from typing import Tuple

from cryptography.hazmat.primitives.asymmetric import dh, types
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
from Crypto.Random import get_random_bytes

class KeyExchangeHandler:
    def load_public_key(self, peer_public_key_bytes: bytes) -> dh.DHPublicKey:
        logging.debug("Loading public key")
        pk = serialization.load_der_public_key(peer_public_key_bytes, backend=default_backend())
        if not isinstance(pk, types.PublicKeyTypes):
            raise TypeError("Invalid public key type")
        if not isinstance(pk, dh.DHPublicKey):
            raise TypeError("Invalid public key type")
        logging.debug("Public key loaded successfully")
        return pk

    def generate_full_key(self, key_half1: bytes, key_half2: bytes, derived_key: bytes) -> bytes:
        combined = key_half1 + key_half2
        salt = get_random_bytes(16)
        logging.debug(f"Combining key halves: {key_half1.hex()} + {key_half2.hex()} with derived key: {derived_key.hex()}")
        logging.debug(f"Using salt: {salt.hex()}")
        full_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            info=b'handshake data',
            backend=default_backend()
        ).derive(combined + derived_key)
        logging.debug(f"Generated full key: {full_key.hex()}")
        return full_key

    def create_initial_keys(self, parameters: dh.DHParameters) -> Tuple[dh.DHPrivateKey, bytes]:
        logging.debug("Generating initial keys")
        private_key = parameters.generate_private_key()
        public_key = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        logging.debug(f"Generated initial keys: {public_key.hex()}")
        return private_key, public_key

    def derive_key_from_shared(self, shared_key: bytes) -> bytes:
        logging.debug(f"Deriving key from shared key: {shared_key.hex()}")
        derived_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b'handshake data',
            backend=default_backend()
        ).derive(shared_key)
        logging.debug(f"Derived key: {derived_key.hex()}")
        return derived_key

    def perform_dh_exchange(self, conn: socket.socket, parameters: dh.DHParameters):
        logging.debug("Starting Diffie-Hellman exchange")
        try:
            private_key, public_key = self.create_initial_keys(parameters)
            logging.debug("Sending public key")
            conn.sendall(public_key)

            peer_public_key_bytes = conn.recv(1024)
            logging.debug(f"Received peer public key: {peer_public_key_bytes.hex()}")
            peer_public_key: dh.DHPublicKey = self.load_public_key(peer_public_key_bytes)

            shared_key = private_key.exchange(peer_public_key)
            logging.debug(f"Shared key: {shared_key.hex()}")
            derived_key = self.derive_key_from_shared(shared_key)
            logging.debug(f"Derived key: {derived_key.hex()}")

            key_half = get_random_bytes(16)
            logging.debug(f"Sending key half: {key_half.hex()}")
            conn.sendall(key_half)
            other_key_half = conn.recv(16)
            logging.debug(f"Received other key half: {other_key_half.hex()}")

            full_key = self.generate_full_key(key_half, other_key_half, derived_key)
            logging.debug(f"Full derived key: {full_key.hex()}")
        except Exception as e:
            logging.error(f"Error during Diffie-Hellman key exchange: {str(e)}")
        finally:
            conn.close()
            logging.debug("Connection closed")
