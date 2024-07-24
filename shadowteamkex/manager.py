import logging

from shadowteamkex.preconnect import PreconnectHandler
from shadowteamkex.kex import KeyExchangeHandler, dh, default_backend
from shadowteamkex.roles import InitiatorRole, ListenerRole

class DiffieHellmanExchangeManager:
    def __init__(self, peer_ip: str):
        self.peer_ip = peer_ip
        self.parameters = dh.generate_parameters(generator=2, key_size=2048, backend=default_backend())
        self.preconnect_handler = PreconnectHandler(peer_ip)
        self.key_exchange_handler = KeyExchangeHandler()

    def negotiate_roles(self):
        return self.preconnect_handler.negotiate_roles()

    def run_role(self, role: str, peer_port: int):
        if role == 'initiator':
            logging.info("Role is initiator, starting client")
            role_instance = InitiatorRole(self.peer_ip, self.parameters, peer_port, self.key_exchange_handler)
        elif role == 'listener':
            logging.info("Role is listener, starting server")
            role_instance = ListenerRole(self.parameters, peer_port, self.key_exchange_handler)
        else:
            logging.error("Failed to determine roles")
            return
        role_instance.run()

    def start_exchange(self):
        roles = self.negotiate_roles()
        if roles:
            role, peer_port = roles
        else:
            logging.error("Uh oh! A fuckywucky happened and ShadowTeamKex had to get in the forever box! Restarting...")
            return self.start_exchange()
        assert role is not None
        assert peer_port is not None
        self.run_role(role, peer_port)
