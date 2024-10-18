import logging
import time

from src.nurapy import NurAPY

logging.basicConfig(level=logging.DEBUG)

api = NurAPY('COM8')
api.ping()