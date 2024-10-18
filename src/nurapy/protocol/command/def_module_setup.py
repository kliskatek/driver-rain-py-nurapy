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
class NurModuleSetup:
    link_freq: ModuleSetupLinkFreq = None
    rx_decoding: ModuleSetupRxDec = None
    tx_level: int = None
    tx_modulation: int = None
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
