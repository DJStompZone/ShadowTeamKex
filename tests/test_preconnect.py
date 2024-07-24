import pytest
from unittest.mock import patch, MagicMock
from shadowteamkex.preconnect import PreconnectHandler

@pytest.fixture
def preconnect_handler():
    return PreconnectHandler('127.0.0.1')

@patch('shadowteamkex.preconnect.socket.socket')
def test_create_preconnect_socket(mock_socket, preconnect_handler):
    udp_socket = preconnect_handler.create_preconnect_socket()
    assert mock_socket.called
    assert udp_socket == mock_socket.return_value

@patch('shadowteamkex.preconnect.socket.socket.sendto')
def test_send_negotiation_packet(mock_sendto, preconnect_handler):
    udp_socket = MagicMock()
    preconnect_handler.send_negotiation_packet(udp_socket)
    assert mock_sendto.called

@patch('shadowteamkex.preconnect.socket.socket.recvfrom', return_value=(b'100,1618325012.000000,some_session_id,17377', None))
def test_receive_negotiation_packet(mock_recvfrom, preconnect_handler):
    udp_socket = MagicMock()
    result = preconnect_handler.receive_negotiation_packet(udp_socket)
    assert result == (100, 1618325012.000000, 'some_session_id', 17377)

@patch('shadowteamkex.preconnect.socket.socket.sendto')
def test_send_handshake_packet(mock_sendto, preconnect_handler):
    udp_socket = MagicMock()
    preconnect_handler.send_handshake_packet(udp_socket)
    assert mock_sendto.called

@patch('shadowteamkex.preconnect.socket.socket.recvfrom', return_value=(b'HANDSHAKE,some_session_id', None))
def test_receive_handshake_packet(mock_recvfrom, preconnect_handler):
    udp_socket = MagicMock()
    preconnect_handler.receive_handshake_packet(udp_socket)
    assert mock_recvfrom.called
