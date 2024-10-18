import logging
import time

from src.nurapy import NurAPY, ModuleSetupFlags, ModuleSetup
from src.nurapy.protocol.command.module_setup import ModuleSetupLinkFreq, ModuleSetupRxDec

logging.basicConfig(level=logging.DEBUG)

api = NurAPY('COM8')
#api.restart()
#time.sleep(4)
api.ping()
api.get_mode()
reader_info = api.get_reader_info()
device_caps = api.get_device_capabilities()
setup = api.get_module_setup(setup_flags=[
    ModuleSetupFlags.LINKFREQ,
    ModuleSetupFlags.RXDEC,
    ModuleSetupFlags.TXLEVEL,
    ModuleSetupFlags.ANTMASKEX,
    ModuleSetupFlags.SELECTEDANT,
    ModuleSetupFlags.ALL
])

new_setup = ModuleSetup()
new_setup.link_freq = ModuleSetupLinkFreq.BLF_256
new_setup.rx_decoding = ModuleSetupRxDec.MILLER_4
new_setup.tx_level = 0
new_setup.antenna_mask = 1
new_setup.selected_antenna = 0
setup = api.set_module_setup(setup_flags=[
    ModuleSetupFlags.LINKFREQ,
    ModuleSetupFlags.RXDEC,
    ModuleSetupFlags.TXLEVEL,
    ModuleSetupFlags.ANTMASK,
    ModuleSetupFlags.SELECTEDANT
], module_setup=new_setup)

api.simple_inventory(session=0, q=4, rounds=100)