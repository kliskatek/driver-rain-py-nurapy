import logging
import time

from src.nurapy import NurAPY

logging.basicConfig(level=logging.DEBUG)

api = NurAPY('COM8')
api.ping()
api.reset()
api.get_mode()
api.get_reader_info()
api.get_device_capabilities()