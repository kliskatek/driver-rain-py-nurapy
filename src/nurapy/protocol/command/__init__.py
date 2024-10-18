import struct
from enum import Enum


class HeaderFlagCodes(Enum):
    RESPONSE = 0x0000
    NOTIFICATION = 0x0001
    INVENTORY_READ_NOTIFICATION = 0x0002


class CommandCode(Enum):
    PING = 1
    RESET = 3
    GET_MODE = 4
    CLEAR_ID_BUFFER = 5
    GET_READER_INFO = 9
    GET_DEVICE_CAPABILITIES = 0xB
    RESTART = 0x14
    GET_MODULE_SETUP = 0x22


def extract_bytes(payload: bytearray, number_of_bytes: int) -> bytearray:
    b = payload[:number_of_bytes]
    del payload[:number_of_bytes]
    return b


def extract_string(payload: bytearray) -> str:
    string_length = payload[0]
    content = payload[1:string_length + 1]
    del payload[:string_length + 1]
    return content.decode('utf-8')


def extract_int8(payload: bytearray) -> int:
    i = struct.unpack('b', bytes([payload[0]]))[0]
    del payload[0]
    return i


def to_int8_bytes(value: int) -> bytes:
    return struct.pack('b', value)


def extract_uint8(payload: bytearray) -> int:
    i = struct.unpack('B', bytes([payload[0]]))[0]
    del payload[0]
    return i


def to_uint8_bytes(value: int) -> bytes:
    return struct.pack('B', value)


def extract_int16(payload: bytearray) -> int:
    i = struct.unpack('<h', payload[:2])[0]
    del payload[:2]
    return i


def to_int16_bytes(value: int) -> bytes:
    return struct.pack('<h', value)


def extract_uint16(payload: bytearray) -> int:
    i = struct.unpack('<H', payload[:2])[0]
    del payload[:2]
    return i


def to_uint16_bytes(value: int) -> bytes:
    return struct.pack('<H', value)


def extract_int32(payload: bytearray) -> int:
    i = struct.unpack('<i', payload[:4])[0]
    del payload[:4]
    return i


def to_int32_bytes(value: int) -> bytes:
    return struct.pack('<i', value)


def extract_uint32(payload: bytearray) -> int:
    i = struct.unpack('<I', payload[:4])[0]
    del payload[:4]
    return i


def to_uint32_bytes(value: int) -> bytes:
    return struct.pack('<I', value)
