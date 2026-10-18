import logging
import queue
import struct
from threading import Thread
from typing import Callable, List

from . import Packet
from .command.get_device_capabilities import parse_get_device_capabilities_response
from .command.get_id_buffer import parse_get_id_buffer_response
from .command.get_id_buffer_meta import parse_get_id_buffer_meta_response, NurTagDataMeta
from .command.get_mode import parse_get_mode_response
from .command import HeaderFlagCodes, StatusCode
from .command.inventory import parse_inventory_response
from .command.inventory_stream import parse_inventory_stream_notification, InventoryStreamNotification
from .command.module_setup import parse_module_setup_response
from .command.get_reader_info import parse_get_reader_info_response
from .. import CommandCode

logger = logging.getLogger(__name__)

HEADER_SIZE = 6


class RxHandler:

    def __init__(self):
        self.buffer = bytearray()
        self.response_queue = queue.Queue()
        self.notification_queue = queue.Queue()
        self.notification_callback = None
        self._callback_thread = Thread(target=self._callback_thread_fxn, daemon=True, name='CallbackThread')
        self._callback_thread.start()

    def set_notification_callback(self, callback: Callable[[InventoryStreamNotification,
                                                            List[NurTagDataMeta]], None]) -> None:
        self.notification_callback = callback

    def _callback_thread_fxn(self) -> None:
        while True:
            notification, tags = self.notification_queue.get()
            if self.notification_callback:
                self.notification_callback(notification, tags)

    def append_data(self, data):
        if data is not None:
            self.buffer += data
            self._try_parse_data()

    def _try_parse_data(self):
        # Packet layout (struct NUR_HEADER in NurProtocol.h):
        #   start(1) payloadLen(2) flags(2) checksum(1) | cmd(1) status(1) data(...) crc(2)
        # payloadLen counts cmd + status + data + crc, so a packet takes
        # HEADER_SIZE + payloadLen bytes. Several packets can arrive in one
        # serial read; every complete packet is consumed even if it cannot be
        # parsed, otherwise it would block the buffer for good.
        while True:
            # Discard data until PREAMBLE
            start = self.buffer.find(bytearray([Packet.START_BYTE]))
            if start < 0:
                self.buffer.clear()
                return
            if start > 0:
                logger.warning('Syching PREAMBLE.')
                del self.buffer[:start]

            # Check if Header available
            if len(self.buffer) < HEADER_SIZE:
                return
            # Checksum validation
            if Packet.checksum(self.buffer[0:5]) != self.buffer[5]:
                logger.warning('Checksum mismatch')
                # Remove START_BYTE
                del self.buffer[0]
                continue
            payload_len = struct.unpack('<H', self.buffer[1:3])[0]
            if payload_len < 3:
                logger.warning('Invalid payload length %d', payload_len)
                del self.buffer[0]
                continue
            packet_len = HEADER_SIZE + payload_len
            # Check if Full packet available
            if len(self.buffer) < packet_len:
                return
            packet = bytes(self.buffer[:packet_len])
            # Remove processed data
            del self.buffer[:packet_len]

            # Check CRC
            crc_rx = struct.unpack('<H', packet[-2:])[0]
            if Packet.crc16(packet[HEADER_SIZE:-2]) != crc_rx:
                logger.warning('CRC mismatch')
                continue
            try:
                self._process_packet(packet)
            except Exception as e:
                logger.error('Error processing packet %s: %s', packet.hex().upper(), e)

    def _process_packet(self, packet: bytes):
        header_flags = struct.unpack('<H', packet[3:5])[0]
        command_value = packet[HEADER_SIZE]
        body = bytearray(packet[HEADER_SIZE + 1:-2])
        if not body:
            logger.warning('Packet without status: %s', packet.hex().upper())
            return
        status_value = body[0]
        payload = body[1:]
        try:
            command = CommandCode(command_value)
        except ValueError:
            command = None

        # The high nibble of the flags is a sequence number and bit 2 asks
        # for an ACK, so test the bits instead of comparing the whole word.
        if header_flags & HeaderFlagCodes.NOTIFICATION.value:
            ir_data = bool(header_flags & HeaderFlagCodes.INVENTORY_READ_NOTIFICATION.value)
            logger.debug('notif cmd=0x%02X flags=0x%04X status=0x%02X ir=%s payload=%s',
                         command_value, header_flags, status_value, ir_data, payload.hex().upper())
            if command is not CommandCode.NOTIFICATION_INVENTORY:
                logger.debug('Ignoring notification 0x%02X', command_value)
                return
            if status_value != StatusCode.SUCCESS.value:
                # Still hand it over without tags: the host ACKs every
                # inventory notification and restarts a stopped stream.
                logger.warning('Inventory notification with status 0x%02X', status_value)
                notification = InventoryStreamNotification(stopped=bool(payload[0]) if payload else False)
                self.notification_queue.put([notification, []])
                return
            self._process_notification(command, payload, ir_data)
            return

        if status_value != StatusCode.SUCCESS.value:
            try:
                logger.error('%s: %s', command.name if command else hex(command_value), StatusCode(status_value).name)
            except ValueError:
                logger.error('%s: status 0x%02X', command.name if command else hex(command_value), status_value)
            # Unblock the waiting command instead of letting it time out.
            self.response_queue.put(None)
            return
        if command is None:
            logger.warning('Ignoring response to unknown command 0x%02X', command_value)
            return
        self._process_response(command, payload)

    def _process_response(self, command: CommandCode, payload: bytearray):
        if command is CommandCode.PING:
            self.response_queue.put(True)
            return
        if command is CommandCode.RESET:
            self.response_queue.put(True)
            return
        if command is CommandCode.RESTART:
            self.response_queue.put(True)
            return
        if command is CommandCode.GET_MODE:
            self.response_queue.put(parse_get_mode_response(payload))
            return
        if command is CommandCode.GET_READER_INFO:
            self.response_queue.put(parse_get_reader_info_response(payload))
            return
        if command is CommandCode.GET_DEVICE_CAPABILITIES:
            self.response_queue.put(parse_get_device_capabilities_response(payload))
            return
        if command is CommandCode.GET_MODULE_SETUP:
            self.response_queue.put(parse_module_setup_response(payload))
            return
        if command is CommandCode.SIMPLE_INVENTORY:
            self.response_queue.put(parse_inventory_response(payload))
            return
        if command is CommandCode.GET_ID_BUFFER:
            self.response_queue.put(parse_get_id_buffer_response(payload))
            return
        if command is CommandCode.GET_ID_BUFFER_META:
            self.response_queue.put(parse_get_id_buffer_meta_response(payload))
            return
        if command is CommandCode.CLEAR_ID_BUFFER:
            self.response_queue.put(True)
            return
        if command is CommandCode.INVENTORY_STREAM:
            self.response_queue.put(True)
            return
        if command is CommandCode.INVREAD_CONFIG:
            self.response_queue.put(True)
            return
        if command is CommandCode.INVENTORY_READ:
            self.response_queue.put(True)
            return
        if command is CommandCode.STOP_ALL_CONT:
            self.response_queue.put(True)
            return

    def _process_notification(self, command: CommandCode, payload: bytearray,
                              ir_data: bool = False):
        if command is CommandCode.NOTIFICATION_INVENTORY:
            self.notification_queue.put(
                parse_inventory_stream_notification(payload, with_ir_data=ir_data)
            )
            return

    def clear_responses(self):
        while True:
            try:
                self.response_queue.get_nowait()
            except queue.Empty:
                return

    def get_response(self, timeout=1):
        try:
            return self.response_queue.get(timeout=timeout)
        except queue.Empty:
            raise TimeoutError
