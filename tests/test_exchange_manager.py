import pytest
from unittest.mock import patch, MagicMock
from shadowteamkex.manager import DiffieHellmanExchangeManager
from shadowteamkex.preconnect import PreconnectHandler
from shadowteamkex.kex import KeyExchangeHandler

@pytest.fixture
def exchange_manager():
    return DiffieHellmanExchangeManager('127.0.0.1')

@patch.object(PreconnectHandler, 'negotiate_roles', return_value=('initiator', 17377))
def test_negotiate_roles(mock_negotiate_roles, exchange_manager):
    roles = exchange_manager.negotiate_roles()
    assert roles == ('initiator', 17377)

@patch.object(DiffieHellmanExchangeManager, 'run_role')
@patch.object(PreconnectHandler, 'negotiate_roles', return_value=('initiator', 17377))
def test_start_exchange(mock_negotiate_roles, mock_run_role, exchange_manager):
    exchange_manager.start_exchange()
    assert mock_run_role.called

@patch('threading.Thread.start')
def test_run_role_initiator(mock_thread_start, exchange_manager):
    exchange_manager.run_role('initiator', 17377)
    assert mock_thread_start.called

@patch('threading.Thread.start')
def test_run_role_listener(mock_thread_start, exchange_manager):
    exchange_manager.run_role('listener', 17377)
    assert mock_thread_start.called
