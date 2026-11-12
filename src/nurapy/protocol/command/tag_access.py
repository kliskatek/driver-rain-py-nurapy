"""NUR_CMD_READ (0x33) and NUR_CMD_WRITE (0x34): read and write tag memory.

Payload as in nur_nurapi_micro (NurMicroApi.c, WriteCommonSingulationBlock, NurApiReadTag, NurApiWriteTag),
little-endian:

    uint8_t  flags        RW_SEC (password), RW_SBP (singulation block present)
    uint32_t passwd       0 unless RW_SEC
    [singulation block, if RW_SBP]
    uint8_t  bytestofollow  7 + mask bytes
    uint8_t  bank           memory bank of the Select mask
    uint32_t address        bit address of the mask (32 = start of the EPC, after CRC and PC)
    uint16_t maskbitlen
    uint8_t  mask[]
    [read block]                       [write block]
    uint8_t  bytestofollow  6           uint8_t  bytestofollow  6 + 2 * wordcount
    uint8_t  bank                       uint8_t  bank
    uint32_t word address               uint32_t word address
    uint8_t  wordcount                  uint8_t  wordcount
                                        uint8_t  data[2 * wordcount]   (tag order, MSB of each word first)

The response of a read is the data; the response of a write is empty. On error the status byte is not 0, and with
NUR_ERROR_G2_TAG_RESP the first payload byte is the Gen2 error code of the tag.
"""

import struct
from dataclasses import dataclass
from enum import IntEnum
from typing import Optional

RW_SEC = 1 << 0
RW_SBP = 1 << 1

EPC_MASK_BIT_ADDRESS = 32       # the EPC starts after CRC16 and PC


class Bank(IntEnum):
    RESERVED = 0
    EPC = 1
    TID = 2
    USER = 3


NUR_ERRORS = {
    0x01: 'INVALID_COMMAND', 0x02: 'INVALID_LENGTH', 0x03: 'PARAMETER_OUT_OF_RANGE', 0x04: 'RECEIVE_TIMEOUT',
    0x05: 'INVALID_PARAMETER', 0x06: 'PROGRAM_FAILED', 0x07: 'PARAMETER_MISMATCH', 0x08: 'HW_MISMATCH',
    0x0A: 'PAGE_PROGRAM', 0x0B: 'CRC_CHECK', 0x0C: 'CRC_MISMATCH', 0x0D: 'NOT_READY', 0x0E: 'APP_NOT_PRESENT',
    0x10: 'GENERAL', 0x11: 'RESEND_PACKET',
    0x20: 'NO_TAG', 0x21: 'RESP_AIR', 0x22: 'G2_SELECT', 0x23: 'MISSING_SELDATA', 0x24: 'G2_ACCESS',
    0x30: 'G2_READ', 0x31: 'G2_RD_PART', 0x40: 'G2_WRITE', 0x41: 'G2_WR_PART', 0x42: 'G2_TAG_RESP',
    0x50: 'G2_SPECIAL', 0x60: 'READER_HW', 0x61: 'BAD_ANTENNA', 0x62: 'LOW_VOLTAGE', 0x63: 'OVER_TEMP',
}
NUR_ERROR_G2_TAG_RESP = 0x42

# Gen2 tag error codes (EPC Gen2 annex I)
G2_TAG_ERRORS = {
    0x00: 'OTHER', 0x01: 'NOT_SUPPORTED', 0x02: 'INSUFFICIENT_PRIVILEGES', 0x03: 'MEMORY_OVERRUN',
    0x04: 'MEMORY_LOCKED', 0x05: 'CRYPTO_SUITE', 0x06: 'NOT_ENCAPSULATED', 0x07: 'RESPONSE_BUFFER_OVERFLOW',
    0x08: 'SECURITY_TIMEOUT', 0x0B: 'INSUFFICIENT_POWER', 0x0F: 'NON_SPECIFIC',
}


@dataclass
class NurError:
    """A command answered with an error status (instead of data)."""
    status: int
    tag_error: Optional[int] = None

    def __bool__(self):
        return False

    def __str__(self):
        text = NUR_ERRORS.get(self.status, f'0x{self.status:02X}')
        if self.tag_error is not None:
            text += ' (tag: ' + G2_TAG_ERRORS.get(self.tag_error, f'0x{self.tag_error:02X}') + ')'
        return text


def _common_block(epc: Optional[bytes], password: Optional[int]) -> bytearray:
    flags = 0
    if password is not None:
        flags |= RW_SEC
    if epc:
        flags |= RW_SBP
    payload = bytearray(struct.pack('<BI', flags, password or 0))
    if epc:
        payload += struct.pack('<BBIH', 7 + len(epc), Bank.EPC, EPC_MASK_BIT_ADDRESS, len(epc) * 8)
        payload += bytes(epc)
    return payload


def build_read_payload(bank: Bank, word_address: int, word_count: int,
                       epc: Optional[bytes] = None, password: Optional[int] = None) -> bytearray:
    if not 1 <= word_count <= 255:
        raise ValueError('word_count must be 1..255')
    payload = _common_block(epc, password)
    payload += struct.pack('<BBIB', 6, int(bank), word_address, word_count)
    return payload


def build_write_payload(bank: Bank, word_address: int, data: bytes,
                        epc: Optional[bytes] = None, password: Optional[int] = None) -> bytearray:
    if len(data) % 2 or not 2 <= len(data) <= 244:
        raise ValueError('data must be whole words, 1..122 words')
    payload = _common_block(epc, password)
    payload += struct.pack('<BBIB', 6 + len(data), int(bank), word_address, len(data) // 2)
    payload += bytes(data)
    return payload
