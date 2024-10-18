# SPDX-FileCopyrightText: 2024-present Iz2k <ibon@zalbide.com>
#
# SPDX-License-Identifier: MIT
import inspect
import logging
import time
from threading import Thread
from typing import Callable, Any

from .protocol import Packet, CommandCode
from .protocol.rx_handler import RxHandler
from .transport.serial import SerialPort

logger = logging.getLogger(__name__)


class NurAPY:

    def __init__(self, connection_string=None):
        self.transport = None
        self._rx_handler = RxHandler()
        if connection_string is not None:
            self.connect(connection_string)

    def set_notification_callback(self, notification_callback: Callable[[Any], None]):
        self._rx_handler.set_notification_callback(notification_callback)

    def connect(self, connection_string) -> bool:
        # TODO: Parse connection string to determine transport type
        self.transport = SerialPort(read_callback=self._rx_handler.append_data)
        return self.transport.connect(connection_string)

    def is_connected(self) -> bool:
        if self.transport is None:
            return False
        return self.transport.is_connected()

    def disconnect(self) -> bool:
        if not self.is_connected():
            logger.info('RedRcp already disconnected.')
            return True
        try:
            self.transport.disconnect()
            logger.info('RedRcp successfully disconnected.')
            return True
        except Exception as e:
            logger.warning(e)
            return False

    def _execute_command(self, command_packet: Packet):
        if not self.transport.is_connected():
            logger.info('Transport is disconnected.')
            return None

        logger.info('TX -> ' + command_packet.get_command_code().name)
        self.transport.write(command_packet.bytes())
        try:
            response = self._rx_handler.get_response()
            logger.info('RX <- ' + str(response))
            return response
        except TimeoutError:
            logger.info('Timeout executing ' + command_packet.get_command_code().name)
            return None

    def ping(self):
        packet = Packet(command_code=CommandCode.PING, args=[0x01, 0x00, 0x00, 0x00])
        response = self._execute_command(packet)
        return response

    def reset(self):
        packet = Packet(command_code=CommandCode.RESET, args=[])
        response = self._execute_command(packet)
        return response

    def get_mode(self):
        packet = Packet(command_code=CommandCode.GET_MODE, args=[])
        response = self._execute_command(packet)
        return response

    def get_reader_info(self):
        packet = Packet(command_code=CommandCode.GET_READER_INFO, args=[])
        response = self._execute_command(packet)
        return response

    def get_device_capabilities(self):
        packet = Packet(command_code=CommandCode.GET_DEVICE_CAPABILITIES, args=[])
        response = self._execute_command(packet)
        return response
