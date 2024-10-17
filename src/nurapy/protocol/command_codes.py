from enum import Enum


class CommandCode(Enum):
    PING = 1
    RESET = 3
    GET_MODE = 4
    CLEAR_ID_BUFFER = 5