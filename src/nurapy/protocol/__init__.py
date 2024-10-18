from enum import Enum
from typing import List, Any

from crccheck.crc import Crc16Ibm3740

from .command_codes import CommandCode


class Packet:
    START_BYTE = 0xA5

    def __init__(self, command_code: CommandCode, args: List[Any]):
        self.command_buffer = bytearray()
        self.command_buffer.append(Packet.START_BYTE)
        self.command_buffer += int(0).to_bytes(2, 'little')  # Fake length
        self.command_buffer += int(0).to_bytes(2, 'little')  # Flag word
        self.command_buffer.append(0x00)  # Fake checksum
        self.command_buffer.append(command_code.value)
        arg_length = 0
        for arg in args:
            if isinstance(arg, list):
                for item in arg:
                    self.command_buffer.append(item)
                    arg_length += 1
            elif isinstance(arg, bytes):
                for item in arg:
                    self.command_buffer.append(item)
                    arg_length += 1
            elif isinstance(arg, bytearray):
                self.command_buffer += bytearray(arg)
                arg_length += len(arg)
            elif isinstance(arg, Enum):
                self.command_buffer.append(arg.value)
                arg_length += 1
            else:
                self.command_buffer.append(arg)
                arg_length += 1

        # Get CRC16 without header
        crc16 = self.crc16(self.command_buffer[6:])
        self.command_buffer += int(crc16).to_bytes(2, 'little')

        # Set real command payload length (without 6byte header)
        self.command_buffer[1:3] = (len(self.command_buffer) - 6).to_bytes(2, 'little')
        # Set real checksum
        self.command_buffer[5] = Packet.checksum(self.command_buffer[:5])

    def bytes(self):
        return self.command_buffer

    def get_command_code(self) -> CommandCode | None:
        if len(self.command_buffer) < 6:
            return None
        return CommandCode(self.command_buffer[6])

    def __str__(self):
        return self.command_buffer.hex(sep=' ').upper()

    @staticmethod
    def checksum(data: bytes):
        cs = 0xFF
        for byte in data:
            cs ^= byte
        return cs & 0xFF

    @staticmethod
    def crc16(data: bytes):
        crc = Crc16Ibm3740.calc(data)
        return crc
