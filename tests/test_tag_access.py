"""NUR_CMD_READ / NUR_CMD_WRITE: payload packing (as nur_nurapi_micro does) and response handling."""
import struct
import time

from nurapy.protocol import Packet
from nurapy.protocol.command import CommandCode
from nurapy.protocol.command.tag_access import Bank, NurError, build_read_payload, build_write_payload
from nurapy.protocol.rx_handler import RxHandler

EPC = bytes.fromhex('E2801160600002054F2A0B11')       # 96-bit EPC


def test_read_payload_singulated_by_epc():
    p = build_read_payload(Bank.USER, 0x100, 4, epc=EPC)
    expected = (bytes([0x02]) + struct.pack('<I', 0)                    # flags RW_SBP, no password
                + bytes([7 + 12, 1]) + struct.pack('<I', 32) + struct.pack('<H', 96) + EPC
                + bytes([6, 3]) + struct.pack('<I', 0x100) + bytes([4]))
    assert bytes(p) == expected


def test_read_payload_without_singulation_with_password():
    p = build_read_payload(Bank.TID, 0, 2, password=0x12345678)
    assert bytes(p) == bytes([0x01, 0x78, 0x56, 0x34, 0x12, 6, 2, 0, 0, 0, 0, 2])


def test_write_payload():
    data = bytes.fromhex('ABCD1234')
    p = build_write_payload(Bank.USER, 0x10, data, epc=EPC)
    expected = (bytes([0x02]) + struct.pack('<I', 0)
                + bytes([19, 1]) + struct.pack('<I', 32) + struct.pack('<H', 96) + EPC
                + bytes([6 + 4, 3]) + struct.pack('<I', 0x10) + bytes([2]) + data)
    assert bytes(p) == expected


def test_write_payload_rejects_odd_bytes():
    try:
        build_write_payload(Bank.USER, 0, b'\x01')
    except ValueError:
        return
    raise AssertionError('odd byte count accepted')


def _response(command: CommandCode, status: int, data: bytes = b'') -> bytes:
    """A reader response has the same framing as a command: A5, length, flags 0, checksum, cmd, status, data, CRC."""
    return bytes(Packet(command_code=command, args=[bytes([status]) + data]).bytes())


def _get(rx: RxHandler):
    return rx.get_response(timeout=1)


def test_read_response_gives_the_data():
    rx = RxHandler()
    rx.append_data(_response(CommandCode.READ, 0, bytes.fromhex('11223344')))
    assert _get(rx) == bytes.fromhex('11223344')


def test_tag_error_is_returned_and_does_not_block_the_buffer():
    rx = RxHandler()
    # tag answered "memory locked" (NUR_ERROR_G2_TAG_RESP + Gen2 error 0x04), then a good write
    rx.append_data(_response(CommandCode.WRITE, 0x42, bytes([0x04])) + _response(CommandCode.WRITE, 0))
    err = _get(rx)
    assert isinstance(err, NurError) and not err
    assert err.status == 0x42 and err.tag_error == 0x04
    assert 'MEMORY_LOCKED' in str(err)
    assert _get(rx) is True


def test_error_of_other_commands_gives_none_and_the_next_packet_still_arrives():
    rx = RxHandler()
    # an inventory with no tags (NO_TAG) answers None; the read right behind it is not lost
    rx.append_data(_response(CommandCode.SIMPLE_INVENTORY, 0x20) + _response(CommandCode.READ, 0, b'\xAA\xBB'))
    time.sleep(0.05)
    assert _get(rx) is None
    assert _get(rx) == b'\xAA\xBB'
