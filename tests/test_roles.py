import pytest
from unittest.mock import patch, MagicMock
from shadowteamkex.roles import ListenerRole, InitiatorRole
from shadowteamkex.kex import KeyExchangeHandler, dh, default_backend

@pytest.fixture
def dh_parameters():
    return dh.generate_parameters(generator=2, key_size=2048, backend=default_backend())

@pytest.fixture
def key_exchange_handler():
    return KeyExchangeHandler()

@pytest.fixture
def listener_role(dh_parameters, key_exchange_handler):
    return ListenerRole(dh_parameters, 17377, key_exchange_handler)

@pytest.fixture
def initiator_role(dh_parameters, key_exchange_handler):
    return InitiatorRole('127.0.0.1', dh_parameters, 17377, key_exchange_handler)

@patch('shadowteamkex.roles.socket.socket')
@patch('threading.Thread.start')
def test_listener_role_run(mock_thread_start, mock_socket, listener_role):
    listener_role.run()
    assert mock_thread_start.called

@patch('shadowteamkex.roles.socket.socket.connect')
@patch.object(KeyExchangeHandler, 'perform_dh_exchange')
def test_initiator_role_run(mock_perform_dh_exchange, mock_connect, initiator_role):
    initiator_role.run()
    assert mock_connect.called
    assert mock_perform_dh_exchange.called
