from struct import pack

PACKET_HEADER = "<ccLB"
PACKET_BYTES_PER_NATION = 3
PACKET_NUM_NATIONS = 250
PACKET_GENERAL_INFO = "<BBBBBB{0}sBBBBBBLB{1}BLLB"
PACKET_NATION_INFO_START = 15

PACKED_GAME_REQUEST = pack(
    "<ccssssccccccc",
    b"f",
    b"H",
    b"\a",
    b"\x00",
    b"\x00",
    b"\x00",
    b"=",
    b"\x1e",
    b"\x02",
    b"\x11",
    b"E",
    b"\x05",
    b"\x00",
)
