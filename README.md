# nurapy

[![PyPI - Version](https://img.shields.io/pypi/v/nurapy.svg)](https://pypi.org/project/nurapy)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/nurapy.svg)](https://pypi.org/project/nurapy)
![OS](https://img.shields.io/badge/os-windows%20|%20linux%20|%20macos-olive)
![ARCH](https://img.shields.io/badge/arch-x86%20|%20x64%20|%20arm%20|%20arm64-purple)

-----
*Pure Python driver for NordicID UHF RFID readers*
## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
  - [Connect to the reader](#connect-to-the-reader)
  - [Get basic information about the reader](#get-basic-information-about-the-reader)
  - [Configure the reader](#configure-the-reader)
  - [Perform single synchronous inventory](#perform-single-synchronous-inventory)
  - [Perform continuous asynchronous inventory](#perform-continuous-asynchronous-inventory)
- [License](#license)

## Installation

```console
pip install nurapy
```

## Usage
### Connect to the reader
```python
# Create driver
reader = NurAPY()

# Connect
reader.connect(connection_string='COM8')

# Check connection status
if not reader.ping():
    logging.error('Could not connect to NURAPY')
    exit()

... use the reader ...

# Disconnect reader
reader.disconnect()
```

### Get basic information about the reader
```python
## GET INFO
reader_mode = reader.get_mode()
reader_info = reader.get_reader_info()
device_caps = reader.get_device_capabilities()
current_setup = reader.get_module_setup(setup_flags=[
    ModuleSetupFlags.ALL
])
```
Sample response values:

`
reader_mode = Mode.APPLICATION
`

`
reader_info = NurReaderInfo(serial='K134500382', alt_serial='K134700326', name='STIX', fcc_id='', hw_version='PWM00226', sw_version='5.10.A', dev_build=None, num_gpio=None, num_sensors=0, num_regions=21, num_antennas=1, max_antennas=1)
`

`
device_caps = NurDeviceCaps(dwSize=40, flagSet1=15696847, flagSet2=0, maxTxdBm=27, txAttnStep=1, maxTxmW=500, txSteps=20, szTagBuffer=630, curCfgMaxAnt=1, curCfgMaxGPIO=0, chipVersion=<ReaderChipVersion.AS3993: 2>, moduleType=<ModuleType.NUR_L2_05W: 3>, moduleConfigFlags=4)
`

`
current_setup = ModuleSetup(link_freq=<ModuleSetupLinkFreq.BLF_256: 256000>, rx_decoding=<ModuleSetupRxDec.MILLER_4: 2>, tx_level=0, tx_modulation=<ModuleSetupTxMod.PRASK: 1>, region_id=<ModuleSetupRegion.EU: 0>, inventory_q=2, inventory_session=0, inventory_rounds=0, antenna_mask=1, scan_single_trigger_timeout=500, inventory_trigger_timeout=1000, selected_antenna=0, op_flags=2, inventory_target=<ModuleSetupInvTarget.AB: 2>, inventory_epc_length=255, write_rssi_filter=NurRssiFilter(min=0, max=0), inventory_rssi_filter=NurRssiFilter(min=0, max=0), read_to=500, write_to=500, lock_to=500, kill_to=500, period_setup=<ModuleSetupPowerSave.NOT_IN_USE: 0>, ant_power=[0, -1, -1, -1], power_offset=[-1, 0, 0, 0], antenna_mask_ex=256, autotune=NurAutoTuneSetup(mode=0, threshold_dBm=3), ant_power_ex=[-10, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1], rx_sensitivity=<ModuleSetupRxSens.NOMINAL: 0>)
`

### Configure the reader

```python
## MODULE SETUP
new_setup = ModuleSetup()
new_setup.link_freq = ModuleSetupLinkFreq.BLF_256
new_setup.rx_decoding = ModuleSetupRxDec.MILLER_4
new_setup.tx_level = 0
new_setup.antenna_mask = 1
new_setup.selected_antenna = 0
updated_setup = reader.set_module_setup(setup_flags=[
    ModuleSetupFlags.LINKFREQ,
    ModuleSetupFlags.RXDEC,
    ModuleSetupFlags.TXLEVEL,
    ModuleSetupFlags.ANTMASK,
    ModuleSetupFlags.SELECTEDANT
], module_setup=new_setup)
```
### Perform single synchronous inventory
```python

# Trigger a simple inventory
inventory_response = reader.simple_inventory()
if inventory_response.tags_in_memory:
    # Get data of read tags
    tags = reader.get_id_buffer_with_metadata(clear=True)
    logging.info(tags)
```
### Perform continuous asynchronous inventory

```python

def my_notification_callback(inventory_stream_notification: InventoryStreamNotification,
                             notified_tags: List[NurTagDataMeta]):
    # If stream stopped, restart
    if inventory_stream_notification.stopped:
        logging.info('Restarting inventory stream')
        reader.start_inventory_stream()
    for tag in notified_tags:
        logging.info(tag)
    reader.clear_notified_tags()


# Configure the callback
reader.set_notification_callback(my_notification_callback)

# Start inventory stream
reader.start_inventory_stream()

# Do other stuff
time.sleep(1)

# Stop inventory stream
reader.stop_inventory_stream()
```
Sample report:

`
inventory_stream_notification = InventoryStreamNotification(stopped=False, rounds=2, collisions=0, last_q=2)
`

`
notified_tags = [NurTagDataMeta(rssi=-51, scaled_rssi=93, timestamp=5, frequency=866300, pc=13312, channel=1, antenna_id=0, epc=bytearray(b'Q\x10\x12\x03(\x000\x00\x00\x00V\x04'))]
`

## License

`nurapy` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
