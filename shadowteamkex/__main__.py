import logging
import os

from shadowteamkex.manager import DiffieHellmanExchangeManager

def main():
    logging.debug("Starting main function")
    peer_ip = os.environ.get("KEX_PEER_IP", '127.0.0.1')
    logging.info(f"Peer IP: {peer_ip}")

    exchange_manager = DiffieHellmanExchangeManager(peer_ip)
    exchange_manager.start_exchange()

if __name__ == "__main__":
    logging.info("Starting up...")
    main()
