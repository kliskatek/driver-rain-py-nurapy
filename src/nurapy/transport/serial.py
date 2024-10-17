import logging
import time
from threading import Thread

import serial
from serial.serialutil import SerialException

logger = logging.getLogger(__name__)


class SerialPort:
    def __init__(self, port=None, read_callback=None):
        self.read_callback = read_callback
        self.serial = serial.Serial(
            baudrate=115200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS
        )
        self._rx_thread = None
        self._rx_thread_run = False
        if port:
            self.connect(port=port)

    def connect(self, port) -> bool:
        if self.serial.isOpen():
            logger.info('SerialPort already connected.')
            return True
        try:
            self.serial.port = port
            self.serial.open()
            logger.info('SerialPort successfully connected.')
            self._rx_thread = Thread(target=self._rx_thread, daemon=True, name='RxThread')
            self._rx_thread_run = True
            self._rx_thread.start()
            return True
        except Exception as e:
            logger.warning(e)
            return False

    def is_connected(self) -> bool:
        return self.serial.isOpen()

    def disconnect(self) -> bool:
        self._rx_thread_run = False
        if self._rx_thread:
            self._rx_thread.join()
        if not self.is_connected():
            logger.info('SerialPort already disconnected.')
            return True
        try:
            self.serial.close()
            logger.info('SerialPort successfully disconnected.')
            return True
        except Exception as e:
            logger.warning(e)
            return False

    def write(self, data: bytes):
        self.serial.write(data)

    def set_read_callback(self, callback):
        self.read_callback = callback

    def _read(self) -> bytes | None:
        try:
            data = self.serial.read_all()
            if len(data) > 0:
                logger.debug('RX << ' + str(data.hex(sep=' ').upper()))
                return data
        except SerialException:
            logger.info('SerialPort disconnected.')
            self.serial.close()

    def _rx_thread(self):
        while self._rx_thread_run:
            if self.is_connected():
                data = self._read()
                if data is not None:
                    if len(data) > 0:
                        logger.debug('RX << ' + str(data.hex(sep=' ').upper()))
                        if self.read_callback:
                            self.read_callback(data)
            time.sleep(0.001)
