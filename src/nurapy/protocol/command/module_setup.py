import struct

from src.nurapy.protocol.command import extract_uint32, extract_uint8, extract_uint16, extract_int8, to_uint8_bytes, \
    to_uint32_bytes, to_uint16_bytes, to_int8_bytes
from dataclasses import dataclass
from enum import Enum
from typing import List

from dataclasses_json import dataclass_json


class ModuleSetupFlags(Enum):
    LINKFREQ = (1 << 0)  # linkFreq field in struct NUR_MODULESETUP is valid */
    RXDEC = (1 << 1)  # rxDecoding field in struct NUR_MODULESETUP is valid */
    TXLEVEL = (1 << 2)  # txLevel field in struct NUR_MODULESETUP is valid */
    TXMOD = (1 << 3)  # txModulation field in struct NUR_MODULESETUP is valid */
    REGION = (1 << 4)  # regionId field in struct NUR_MODULESETUP is valid */
    INVQ = (1 << 5)  # inventoryQ field in struct NUR_MODULESETUP is valid */
    INVSESSION = (1 << 6)  # inventorySession field in struct NUR_MODULESETUP is valid */
    INVROUNDS = (1 << 7)  # inventoryRounds field in struct NUR_MODULESETUP is valid */
    ANTMASK = (1 << 8)  # antennaMask field in struct NUR_MODULESETUP is valid */
    SCANSINGLETO = (1 << 9)  # scanSingleTriggerTimeout field in struct NUR_MODULESETUP is valid */
    INVENTORYTO = (1 << 10)  # inventoryTriggerTimeout field in struct NUR_MODULESETUP is valid */
    SELECTEDANT = (1 << 11)  # selectedAntenna field in struct NUR_MODULESETUP is valid */
    OPFLAGS = (1 << 12)  # opFlags field in struct NUR_MODULESETUP is valid */
    INVTARGET = (1 << 13)  # inventoryTarget field in struct NUR_MODULESETUP is valid */
    INVEPCLEN = (1 << 14)  # inventoryEpcLength field in struct NUR_MODULESETUP is valid */
    READRSSIFILTER = (1 << 15)  # readRssiFilter field in struct NUR_MODULESETUP is valid */
    WRITERSSIFILTER = (1 << 16)  # writeRssiFilter field in struct NUR_MODULESETUP is valid */
    INVRSSIFILTER = (1 << 17)  # inventoryRssiFilter field in struct NUR_MODULESETUP is valid */
    READTIMEOUT = (1 << 18)  # readTO field in struct NUR_MODULESETUP is valid */
    WRITETIMEOUT = (1 << 19)  # writeTO field in struct NUR_MODULESETUP is valid */
    LOCKTIMEOUT = (1 << 20)  # lockTO field in struct NUR_MODULESETUP is valid */
    KILLTIMEOUT = (1 << 21)  # killTO field in struct NUR_MODULESETUP is valid */
    AUTOPERIOD = (1 << 22)  # stixPeriod field in struct NUR_MODULESETUP is valid */
    PERANTPOWER = (1 << 23)  # antPower field in struct NUR_MODULESETUP is valid */
    PERANTOFFSET = (1 << 24)  # powerOffset field in struct NUR_MODULESETUP is valid */
    ANTMASKEX = (1 << 25)  # antennaMaskEx field in struct NUR_MODULESETUP is valid */
    AUTOTUNE = (1 << 26)  # autotune field in struct NUR_MODULESETUP is valid */
    PERANTPOWER_EX = (1 << 27)  # antPowerEx field in struct NUR_MODULESETUP is valid */
    RXSENS = (1 << 28)  # rxSensitivity field in struct NUR_MODULESETUP is valid */

    # ADDED NUR2 7.0
    #RFPROFILE = (1 << 29)  # rfProfile field in struct NUR_MODULESETUP is valid */

    # ADDED NUR2 7.5, NanoNur 10.2
    #TO_SLEEP_TIME = (1 << 30)  # toSleepTime field in struct NUR_MODULESETUP is valid */

    ALL = ((1 << 29) - 1)  # All setup flags in the structure. */


class ModuleSetupLinkFreq(Enum):
    BLF_160 = 160000
    BLF_256 = 256000
    BLF_320 = 320000


class ModuleSetupRxDec(Enum):
    FM0 = 0
    MILLER_2 = 1
    MILLER_4 = 2
    MILLER_8 = 3


class ModuleSetupTxMod(Enum):
    ASK = 0
    PRASK = 1


class ModuleSetupRegion(Enum):
    EU = 0
    FCC = 1
    PRC = 2
    Malaysia = 3
    Brazil = 4
    Australia = 5
    NewZealand = 6
    Japan_250mW_LBT = 7
    Japan_500mW_DRM = 8
    Korea_LBT = 9
    India = 10
    Russia = 11
    Vietnam = 12
    Singapore = 13
    Thailand = 14
    Philippines = 15
    Morocco = 16
    Peru = 17


class ModuleSetupInvTarget(Enum):
    A = 0
    B = 1
    AB = 2


class ModuleSetupPowerSave(Enum):
    NOT_IN_USE = 0
    MAX_1000MS_QUIET_BETWEEN_INVENTORIES = 1
    MAX_500MS_QUIET_BETWEEN_INVENTORIES = 2
    MAX_100MS_QUIET_BETWEEN_INVENTORIES = 3


class ModuleSetupRxSens(Enum):
    NOMINAL = 0
    LOW = 1
    HIGH = 2


class NurRssiFilter:
    min: int = None
    max: int = None


class NurAutoTuneSetup:
    mode: int = None
    threshold_dBm: int = None


@dataclass_json
@dataclass
class ModuleSetup:
    link_freq: ModuleSetupLinkFreq = None
    rx_decoding: ModuleSetupRxDec = None
    tx_level: int = None
    tx_modulation: ModuleSetupTxMod = None
    region_id: ModuleSetupRegion = None
    inventory_q: int = None
    inventory_session: int = None
    inventory_rounds: int = None
    antenna_mask: int = None
    scan_single_trigger_timeout: int = None
    inventory_trigger_timeout: int = None
    selected_antenna: int = None
    op_flags: int = None
    inventory_target: ModuleSetupInvTarget = None
    inventory_epc_length: int = None
    read_rssi_filter = None
    write_rssi_filter: NurRssiFilter = None
    inventory_rssi_filter: NurRssiFilter = None
    read_to: int = None
    write_to: int = None
    lock_to: int = None
    kill_to: int = None
    period_setup: ModuleSetupPowerSave = None
    ant_power: List[int] = None
    power_offset: List[int] = None
    antenna_mask_ex: int = None
    autotune: NurAutoTuneSetup = None
    ant_power_ex: List[int] = None
    rx_sensitivity: ModuleSetupRxSens = None
    #rf_profile: int = None
    #to_sleep_time: int = None


def parse_module_setup_response(payload: bytearray):
    module_setup = ModuleSetup()
    setup_flags = extract_uint32(payload)
    if setup_flags & ModuleSetupFlags.LINKFREQ.value:
        module_setup.link_freq = ModuleSetupLinkFreq(extract_uint32(payload))
    if setup_flags & ModuleSetupFlags.RXDEC.value:
        module_setup.rx_decoding = ModuleSetupRxDec(extract_uint8(payload))
    if setup_flags & ModuleSetupFlags.TXLEVEL.value:
        module_setup.tx_level = extract_uint8(payload)
    if setup_flags & ModuleSetupFlags.TXMOD.value:
        module_setup.tx_modulation = ModuleSetupTxMod(extract_uint8(payload))
    if setup_flags & ModuleSetupFlags.REGION.value:
        module_setup.region_id = ModuleSetupRegion(extract_uint8(payload))
    if setup_flags & ModuleSetupFlags.INVQ.value:
        module_setup.inventory_q = extract_uint8(payload)
    if setup_flags & ModuleSetupFlags.INVSESSION.value:
        module_setup.inventory_session = extract_uint8(payload)
    if setup_flags & ModuleSetupFlags.INVROUNDS.value:
        module_setup.inventory_rounds = extract_uint8(payload)
    if setup_flags & ModuleSetupFlags.ANTMASK.value:
        module_setup.antenna_mask = extract_uint8(payload)
    if setup_flags & ModuleSetupFlags.SCANSINGLETO.value:
        module_setup.scan_single_trigger_timeout = extract_uint16(payload)
    if setup_flags & ModuleSetupFlags.INVENTORYTO.value:
        module_setup.inventory_trigger_timeout = extract_uint16(payload)
    if setup_flags & ModuleSetupFlags.SELECTEDANT.value:
        module_setup.selected_antenna = extract_uint8(payload)
    if setup_flags & ModuleSetupFlags.OPFLAGS.value:
        module_setup.op_flags = extract_uint32(payload)
    if setup_flags & ModuleSetupFlags.INVTARGET.value:
        module_setup.inventory_target = ModuleSetupInvTarget(extract_uint8(payload))
    if setup_flags & ModuleSetupFlags.INVEPCLEN.value:
        module_setup.inventory_epc_length = extract_uint8(payload)
    if setup_flags & ModuleSetupFlags.READRSSIFILTER.value:
        module_setup.read_rssi_filter = NurRssiFilter()
        module_setup.read_rssi_filter.min = extract_int8(payload)
        module_setup.read_rssi_filter.max = extract_int8(payload)
    if setup_flags & ModuleSetupFlags.WRITERSSIFILTER.value:
        module_setup.write_rssi_filter = NurRssiFilter()
        module_setup.write_rssi_filter.min = extract_int8(payload)
        module_setup.write_rssi_filter.max = extract_int8(payload)
    if setup_flags & ModuleSetupFlags.INVRSSIFILTER.value:
        module_setup.inventory_rssi_filter = NurRssiFilter()
        module_setup.inventory_rssi_filter.min = extract_int8(payload)
        module_setup.inventory_rssi_filter.max = extract_int8(payload)
    if setup_flags & ModuleSetupFlags.READTIMEOUT.value:
        module_setup.read_to = extract_uint16(payload)
    if setup_flags & ModuleSetupFlags.WRITETIMEOUT.value:
        module_setup.write_to = extract_uint16(payload)
    if setup_flags & ModuleSetupFlags.LOCKTIMEOUT.value:
        module_setup.lock_to = extract_uint16(payload)
    if setup_flags & ModuleSetupFlags.KILLTIMEOUT.value:
        module_setup.kill_to = extract_uint16(payload)
    if setup_flags & ModuleSetupFlags.AUTOPERIOD.value:
        module_setup.period_setup = ModuleSetupPowerSave(extract_uint8(payload))
    if setup_flags & ModuleSetupFlags.PERANTPOWER.value:
        module_setup.ant_power = []
        for i in range(4):
            module_setup.ant_power.append(extract_int8(payload))
    if setup_flags & ModuleSetupFlags.PERANTOFFSET.value:
        module_setup.power_offset = []
        for i in range(4):
            module_setup.power_offset.append(extract_int8(payload))
    if setup_flags & ModuleSetupFlags.ANTMASKEX.value:
        module_setup.antenna_mask_ex = extract_uint32(payload)
    if setup_flags & ModuleSetupFlags.AUTOTUNE.value:
        module_setup.autotune = NurAutoTuneSetup()
        module_setup.autotune.mode = extract_uint8(payload)
        module_setup.autotune.threshold_dBm = extract_uint8(payload)
    if setup_flags & ModuleSetupFlags.PERANTPOWER_EX.value:
        module_setup.ant_power_ex = []
        for i in range(32):
            module_setup.ant_power_ex.append(extract_int8(payload))
    if setup_flags & ModuleSetupFlags.RXSENS.value:
        dummy_byte = extract_int8(payload)
        module_setup.rx_sensitivity = ModuleSetupRxSens(extract_int8(payload))

    return module_setup


def populate_module_setup_args(setup_flags: int, module_setup: ModuleSetup):
    args = [struct.pack('I', setup_flags)]
    if setup_flags & ModuleSetupFlags.LINKFREQ.value:
        args.append(to_uint32_bytes(module_setup.link_freq.value))
    if setup_flags & ModuleSetupFlags.RXDEC.value:
        args.append(to_uint8_bytes(module_setup.rx_decoding.value))
    if setup_flags & ModuleSetupFlags.TXLEVEL.value:
        args.append(to_uint8_bytes(module_setup.tx_level))
    if setup_flags & ModuleSetupFlags.TXMOD.value:
        args.append(to_uint8_bytes(module_setup.tx_modulation.value))
    if setup_flags & ModuleSetupFlags.REGION.value:
        args.append(to_uint8_bytes(module_setup.region_id.value))
    if setup_flags & ModuleSetupFlags.INVQ.value:
        args.append(to_uint8_bytes(module_setup.inventory_q))
    if setup_flags & ModuleSetupFlags.INVSESSION.value:
        args.append(to_uint8_bytes(module_setup.inventory_session))
    if setup_flags & ModuleSetupFlags.INVROUNDS.value:
        args.append(to_uint8_bytes(module_setup.inventory_rounds))
    if setup_flags & ModuleSetupFlags.ANTMASK.value:
        args.append(to_uint8_bytes(module_setup.antenna_mask))
    if setup_flags & ModuleSetupFlags.SCANSINGLETO.value:
        args.append(to_uint16_bytes(module_setup.scan_single_trigger_timeout))
    if setup_flags & ModuleSetupFlags.INVENTORYTO.value:
        args.append(to_uint16_bytes(module_setup.inventory_trigger_timeout))
    if setup_flags & ModuleSetupFlags.SELECTEDANT.value:
        args.append(to_uint8_bytes(module_setup.selected_antenna))
    if setup_flags & ModuleSetupFlags.OPFLAGS.value:
        args.append(to_uint32_bytes(module_setup.op_flags))
    if setup_flags & ModuleSetupFlags.INVTARGET.value:
        args.append(to_uint8_bytes(module_setup.inventory_target.value))
    if setup_flags & ModuleSetupFlags.INVEPCLEN.value:
        args.append(to_uint8_bytes(module_setup.inventory_epc_length))
    if setup_flags & ModuleSetupFlags.READRSSIFILTER.value:
        args.append(to_uint8_bytes(module_setup.read_rssi_filter.min))
        args.append(to_uint8_bytes(module_setup.read_rssi_filter.max))
    if setup_flags & ModuleSetupFlags.WRITERSSIFILTER.value:
        args.append(to_uint8_bytes(module_setup.write_rssi_filter.min))
        args.append(to_uint8_bytes(module_setup.write_rssi_filter.max))
    if setup_flags & ModuleSetupFlags.INVRSSIFILTER.value:
        args.append(to_uint8_bytes(module_setup.inventory_rssi_filter.min))
        args.append(to_uint8_bytes(module_setup.inventory_rssi_filter.max))
    if setup_flags & ModuleSetupFlags.READTIMEOUT.value:
        args.append(to_uint16_bytes(module_setup.read_to))
    if setup_flags & ModuleSetupFlags.WRITETIMEOUT.value:
        args.append(to_uint16_bytes(module_setup.write_to))
    if setup_flags & ModuleSetupFlags.LOCKTIMEOUT.value:
        args.append(to_uint16_bytes(module_setup.lock_to))
    if setup_flags & ModuleSetupFlags.KILLTIMEOUT.value:
        args.append(to_uint16_bytes(module_setup.kill_to))
    if setup_flags & ModuleSetupFlags.AUTOPERIOD.value:
        args.append(to_uint16_bytes(module_setup.period_setup.value))
    if setup_flags & ModuleSetupFlags.PERANTPOWER.value:
        for i in range(4):
            args.append(to_int8_bytes(module_setup.ant_power[i]))
    if setup_flags & ModuleSetupFlags.PERANTOFFSET.value:
        for i in range(4):
            args.append(to_int8_bytes(module_setup.power_offset[i]))
    if setup_flags & ModuleSetupFlags.ANTMASKEX.value:
        args.append(to_uint32_bytes(module_setup.antenna_mask_ex))
    if setup_flags & ModuleSetupFlags.AUTOTUNE.value:
        args.append(to_uint8_bytes(module_setup.autotune.mode))
        args.append(to_uint8_bytes(module_setup.autotune.threshold_dBm))
    if setup_flags & ModuleSetupFlags.PERANTPOWER_EX.value:
        for i in range(32):
            args.append(to_int8_bytes(module_setup.ant_power_ex[i]))
    if setup_flags & ModuleSetupFlags.RXSENS.value:
        args.append(0xFF)
        args.append(to_int8_bytes(module_setup.rx_sensitivity.value))

    return args
