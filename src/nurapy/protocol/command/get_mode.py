from enum import Enum


class Mode(Enum):
    APPLICATION = 'A'
    BOOTLOADER = 'B'


def parse_get_mode_response(payload: bytearray) -> Mode:
    return Mode(chr(payload[0]))
