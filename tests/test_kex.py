import pytest
from unittest.mock import patch, MagicMock
from shadowteamkex.kex import KeyExchangeHandler, dh, default_backend

@pytest.fixture
def key_exchange_handler():
    return KeyExchangeHandler()

@pytest.fixture
def dh_parameters():
    return dh.generate_parameters(generator=2, key_size=2048, backend=default_backend())

def test_create_initial_keys(key_exchange_handler, dh_parameters):
    private_key, public_key = key_exchange_handler.create_initial_keys(dh_parameters)
    assert private_key is not None
    assert public_key is not None

def test_generate_full_key(key_exchange_handler):
    key_half1 = b'1234567890123456'
    key_half2 = b'6543210987654321'
    derived_key = b'key_for_testing_purposes_only_'
    full_key = key_exchange_handler.generate_full_key(key_half1, key_half2, derived_key)
    assert full_key is not None

def test_derive_key_from_shared(key_exchange_handler):
    shared_key = b'shared_key_for_testing'
    derived_key = key_exchange_handler.derive_key_from_shared(shared_key)
    assert derived_key is not None

@patch('shadowteamkex.kex.socket.socket')
@patch.object(KeyExchangeHandler, 'create_initial_keys', return_value=(MagicMock(), b'public_key_bytes'))
@patch.object(KeyExchangeHandler, 'load_public_key', return_value=MagicMock())
@patch.object(KeyExchangeHandler, 'derive_key_from_shared', return_value=b'derived_key')
@patch.object(KeyExchangeHandler, 'generate_full_key', return_value=b'full_key')
def test_perform_dh_exchange(mock_generate_full_key, mock_derive_key_from_shared, mock_load_public_key, mock_create_initial_keys, mock_socket, key_exchange_handler, dh_parameters):
    conn = MagicMock()
    key_exchange_handler.perform_dh_exchange(conn, dh_parameters)
    assert mock_create_initial_keys.called
    assert mock_load_public_key.called
    assert mock_derive_key_from_shared.called
    assert mock_generate_full_key.called
