import logging
import struct
from typing import Callable, List

from .protocol import Packet, CommandCode
from ._helpers import to_uint16_bytes, to_uint8_bytes
from .protocol.command.get_device_capabilities import NurDeviceCaps
from .protocol.command.get_id_buffer_meta import NurTagDataMeta
from .protocol.command.get_mode import Mode
from .protocol.command.get_reader_info import NurReaderInfo
from .protocol.command.inventory import InventoryResponse
from .protocol.command.inv_read_config import IrBank, IrType, build_inv_read_config_payload
from .protocol.command.inventory_stream import InventoryStreamNotification
from .protocol.command.module_setup import ModuleSetup, ModuleSetupFlags, populate_module_setup_args
from .protocol.rx_handler import RxHandler
from .transport.serial import SerialPort

logger = logging.getLogger(__name__)


class NurAPY:

    def __init__(self, connection_string=None):
        self.transport = None
        self._rx_handler = RxHandler()
        self.connection_string = connection_string
        if connection_string is not None:
            self.connect(connection_string)

    def set_notification_callback(self, notification_callback: Callable[[InventoryStreamNotification,
                                                                         List[NurTagDataMeta]], None]):
        self._rx_handler.set_notification_callback(notification_callback)

    def connect(self, connection_string=None) -> bool:
        if connection_string:
            self.connection_string = connection_string
        # TODO: Parse connection string to determine transport type (serial only for now)
        self.transport = SerialPort(read_callback=self._rx_handler.append_data)
        return self.transport.connect(connection_string)

    def is_connected(self) -> bool:
        if self.transport is None:
            return False
        return self.transport.is_connected()

    def disconnect(self) -> bool:
        if not self.is_connected():
            logger.info('Transport already disconnected.')
            return True
        try:
            self.transport.disconnect()
            logger.info('Transport successfully disconnected.')
            return True
        except Exception as e:
            logger.warning(e)
            return False

    def _execute_command(self, command_packet: Packet, has_response: bool = True):
        if not self.transport.is_connected():
            if self.connection_string is None:
                logger.info('Transport is disconnected.')
                return None
            if not self.transport.connect(self.connection_string):
                logger.info('Transport is disconnected.')
                return None

        logger.info('TX -> ' + command_packet.get_command_code().name)
        if has_response:
            # A response that arrived after its command timed out would be
            # taken as the answer to this one.
            self._rx_handler.clear_responses()
        self.transport.write(command_packet.bytes())
        if has_response:
            try:
                response = self._rx_handler.get_response()
                logger.info('RX <- ' + str(response))
                return response
            except TimeoutError:
                logger.warning('Timeout executing ' + command_packet.get_command_code().name)
                return None

    def ping(self) -> bool:
        packet = Packet(command_code=CommandCode.PING, args=[0x01, 0x00, 0x00, 0x00])
        response = self._execute_command(packet)
        return response

    def reset(self) -> bool:
        packet = Packet(command_code=CommandCode.RESET, args=[])
        response = self._execute_command(packet)
        return response

    def restart(self) -> bool:
        packet = Packet(command_code=CommandCode.RESTART, args=[])
        response = self._execute_command(packet)
        return response

    def get_mode(self) -> Mode:
        packet = Packet(command_code=CommandCode.GET_MODE, args=[])
        response = self._execute_command(packet)
        return response

    def get_reader_info(self) -> NurReaderInfo:
        packet = Packet(command_code=CommandCode.GET_READER_INFO, args=[])
        response = self._execute_command(packet)
        return response

    def get_device_capabilities(self) -> NurDeviceCaps:
        packet = Packet(command_code=CommandCode.GET_DEVICE_CAPABILITIES, args=[])
        response = self._execute_command(packet)
        return response

    def get_module_setup(self, setup_flags: List[ModuleSetupFlags]) -> ModuleSetup:
        combined_module_setup_flags = 0
        for setup_flag in setup_flags:
            combined_module_setup_flags |= setup_flag.value
        packet = Packet(command_code=CommandCode.GET_MODULE_SETUP, args=[struct.pack('I', combined_module_setup_flags)])
        response = self._execute_command(packet)
        return response

    def set_module_setup(self, setup_flags: List[ModuleSetupFlags], module_setup: ModuleSetup) -> ModuleSetup:
        combined_module_setup_flags = 0
        for setup_flag in setup_flags:
            combined_module_setup_flags |= setup_flag.value
        args = populate_module_setup_args(combined_module_setup_flags, module_setup)
        packet = Packet(command_code=CommandCode.GET_MODULE_SETUP, args=args)
        response = self._execute_command(packet)
        return response

    def simple_inventory(self, q=None, session=None, rounds=None) -> InventoryResponse:
        args = []
        if q is not None and session is not None:
            args.append(q)
            args.append(session)
            if rounds is not None:
                args.append(to_uint8_bytes(rounds))
        packet = Packet(command_code=CommandCode.SIMPLE_INVENTORY, args=args)
        response = self._execute_command(packet)
        return response

    def get_id_buffer(self, clear: bool = False):
        args = []
        if clear:
            args.append(0x01)
        packet = Packet(command_code=CommandCode.GET_ID_BUFFER, args=args)
        response = self._execute_command(packet)
        return response

    def get_id_buffer_with_metadata(self, clear: bool = False):
        args = []
        if clear:
            args.append(0x01)
        packet = Packet(command_code=CommandCode.GET_ID_BUFFER_META, args=args)
        response = self._execute_command(packet)
        return response

    def clear_id_buffer(self):
        packet = Packet(command_code=CommandCode.CLEAR_ID_BUFFER, args=[])
        response = self._execute_command(packet)
        return response

    def start_inventory_stream(self) -> bool:
        packet = Packet(command_code=CommandCode.INVENTORY_STREAM, args=[0x00])
        response = self._execute_command(packet)
        return response

    def stop_inventory_stream(self) -> bool:
        packet = Packet(command_code=CommandCode.INVENTORY_STREAM, args=[])
        response = self._execute_command(packet)
        return response

    def clear_notified_tags(self):
        packet = Packet(command_code=CommandCode.CLEAR_NOTIFIED_TAGS, args=[])
        self._execute_command(packet, has_response=False)

    def set_inventory_read_config(self, active: bool,
                                  bank: IrBank = IrBank.USER,
                                  word_address: int = 0,
                                  word_length: int = 0,
                                  ir_type: IrType = IrType.EPC_AND_DATA) -> bool:
        """Configure embedded Read for subsequent inventories.

        Uses NUR_CMD_INVENTORYREAD (0x41) — the opcode this firmware
        accepts. NUR_CMD_INVREADCONFIG (0x23) is rejected as
        INVALID_COMMAND on the M5e/L2-class module used here, but the
        wire format of the parameters is identical, so we reuse the
        same payload builder.

        When `active=True`, every tag reported by the inventory stream
        will carry the requested User/TID/EPC/Reserved-bank read
        alongside its EPC (the notification arrives with
        PACKET_FLAG_IRDATA set). Pass `active=False` to revert to plain
        inventory.
        """
        payload = build_inv_read_config_payload(active, bank, word_address,
                                                word_length, ir_type)
        packet = Packet(command_code=CommandCode.INVENTORY_READ, args=list(payload))
        return self._execute_command(packet)

    def stop_all_cont(self) -> bool:
        packet = Packet(command_code=CommandCode.STOP_ALL_CONT, args=[])
        return self._execute_command(packet)