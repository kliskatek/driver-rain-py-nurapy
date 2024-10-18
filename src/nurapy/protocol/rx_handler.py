import logging
import queue
import struct
import time

from . import Packet
from .header_flag_codes import HeaderFlagCodes
from .. import CommandCode

logger = logging.getLogger(__name__)


class RxHandler:

    def __init__(self):
        self.buffer = bytearray()
        self.response_queue = queue.Queue()
        self.notification_queue = queue.Queue()
        self.inventory_read_notification_queue = queue.Queue()

    def set_notification_callback(self, callback):
        pass

    def append_data(self, data):
        if data is not None:
            self.buffer += data
            self._try_parse_data()

    def _try_parse_data(self):
        try:
            # Discard data until PREAMBLE
            start = self.buffer.find(bytearray([Packet.START_BYTE]))
            if start > 0:
                logger.warning('Syching PREAMBLE.')
                self.buffer = self.buffer[start:]

            # Check if Header available
            while len(self.buffer) > 5:
                # Checksum validation
                checksum_rx = self.buffer[5]
                checksum_calc = Packet.checksum(self.buffer[0:5])
                if checksum_calc != checksum_rx:
                    logger.warning('Checksum mismatch')
                    # Remove START_BYTE
                    del self.buffer[0]
                else:
                    payload_len = struct.unpack('<H', self.buffer[1:3])[0]
                    message_type = HeaderFlagCodes(struct.unpack('<H', self.buffer[3:5])[0])
                    # Check if Full packet available
                    if len(self.buffer) > 5 + payload_len:
                        # Check CRC
                        crc_rx = struct.unpack('<H', self.buffer[7 + payload_len - 3: 7 + payload_len])[0]
                        crc_calc = Packet.crc16(self.buffer[6:7 + payload_len - 3])
                        if crc_calc != crc_rx:
                            logger.warning('CRC mismatch')
                        else:
                            # Extract data
                            command = CommandCode(self.buffer[6])
                            payload = self.buffer[7:7 + payload_len - 3]

                            # Process message
                            if message_type is HeaderFlagCodes.RESPONSE:
                                self._process_response(command, payload)
                            if message_type is HeaderFlagCodes.NOTIFICATION:
                                self._process_notification(command, payload)
                            if message_type is HeaderFlagCodes.INVENTORY_READ_NOTIFICATION:
                                self._process_inventory_read_notification(command, payload)

                        # Remove processed data
                        del self.buffer[0:8 + payload_len]
                    else:
                        # Missing payload data
                        break
        except Exception as e:
            logger.error(e)

    def _process_response(self, command: CommandCode, payload: bytearray):
        if command is CommandCode.PING:
            self.response_queue.put(True)

    def _process_notification(self, command: CommandCode, payload: bytearray):
        pass

    def _process_inventory_read_notification(self, command: CommandCode, payload: bytearray):
        pass

    def get_response(self):
        while self.response_queue.empty():
            time.sleep(0.001)
        return self.response_queue.get()
