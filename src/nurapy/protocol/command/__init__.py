import struct
from enum import Enum


class HeaderFlagCodes(Enum):
    RESPONSE = 0x0000
    NOTIFICATION = 0x0001
    INVENTORY_READ_NOTIFICATION = 0x0002  # PACKET_FLAG_IRDATA


class CommandCode(Enum):
    PING = 1
    CLEAR_NOTIFIED_TAGS = 2
    RESET = 3
    GET_MODE = 4
    CLEAR_ID_BUFFER = 5
    GET_ID_BUFFER = 6
    GET_ID_BUFFER_META = 7
    GET_READER_INFO = 9
    GET_DEVICE_CAPABILITIES = 0xB
    STOP_ALL_CONT = 0x0E
    RESTART = 0x14
    GET_MODULE_SETUP = 0x22
    INVREAD_CONFIG = 0x23   # Configure embedded Read (not supported by some FW)
    SIMPLE_INVENTORY = 0x31
    INVENTORY_STREAM = 0x39
    INVENTORY_READ = 0x41   # Configure embedded Read for following inventories
    NOTIFICATION_INVENTORY = 0x82


class StatusCode(Enum):
    SUCCESS = 0
    INVALID_COMMAND = 1
    INVALID_LENGTH = 2
    PARAMETER_OUT_OF_RANGE = 3
    INVALID_PARAMETER = 5
    CRC_ERROR = 11
    APPLICATION_NOT_PRESENT = 14
