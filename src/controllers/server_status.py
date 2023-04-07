from socket import socket
from struct import pack, unpack
from zlib import decompress

from src.models.server_details import ServerDetails
from src.utils.socket_request_constants import (
    PACKED_GAME_REQUEST,
    PACKET_BYTES_PER_NATION,
    PACKET_GENERAL_INFO,
    PACKET_HEADER,
    PACKET_NUM_NATIONS,
)


def query_game_server(address: str, port: str) -> ServerDetails:
    """
    Takes in an IP Address and a Port and queries the game server directly to retrieve game data

    :param address:
    :param port:
    :return: GameStatus:
    """
    sck = socket()
    sck.settimeout(5.0)

    sck.connect((address, int(port)))

    packed_game_request = PACKED_GAME_REQUEST
    sck.send(packed_game_request)
    server_response = sck.recv(512)
    # send close command
    sck.send(pack(PACKET_HEADER, b"f", b"H", 1, 11))
    sck.close()

    data_array, hours_remaining = parse_raw_server_data(server_response)

    return ServerDetails(
        name=data_array[6].decode().rstrip("\x00"),
        turn=data_array[-3],
        hours_remaining=hours_remaining,
    )


def parse_raw_server_data(result):
    header = unpack(PACKET_HEADER, result[0:7])
    compressed = header[1] == b"J"
    data = decompress(result[10:]) if compressed else result[10:]
    game_name_length = (
        len(data)
        - len(PACKET_GENERAL_INFO.format("", ""))
        - PACKET_BYTES_PER_NATION * PACKET_NUM_NATIONS
        - 6
    )
    data_array = unpack(
        PACKET_GENERAL_INFO.format(
            game_name_length, PACKET_BYTES_PER_NATION * PACKET_NUM_NATIONS
        ),
        data,
    )
    hours_remaining = round(data_array[13] / (1000 * 60 * 60), 2)
    return data_array, hours_remaining
