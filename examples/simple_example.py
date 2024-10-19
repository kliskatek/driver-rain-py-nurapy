import logging
import time

from src.nurapy import NurAPY, ModuleSetupFlags, ModuleSetup
from src.nurapy.protocol.command.module_setup import ModuleSetupLinkFreq, ModuleSetupRxDec

logging.basicConfig(level=logging.DEBUG)

api = NurAPY('COM8')
if not api.ping():
    logging.error('Could not connect to NUR APY')
    exit()
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

inventory_response = api.simple_inventory(session=0, q=4, rounds=100)
if inventory_response.tags_in_memory:
    # Fetch read tags to tag buffer including metadata
    tag_count = api.get_id_buffer_with_metadata(clear=True)

    # Get data of read tags
    #for idx in range(tag_count):
    #tag_data = api.get_tag_data(idx=idx)

# Clear tag buffer
#api.clear_tags()
api.clear_id_buffer()


def my_notification_callback(notification):
    print(notification)
    api.clear_id_buffer(block=False)


api.set_notification_callback(my_notification_callback)
api.start_inventory_stream()
input()
api.stop_inventory_stream()
input()
