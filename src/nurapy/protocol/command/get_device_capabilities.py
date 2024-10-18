import struct
from dataclasses import dataclass
from enum import Enum

from dataclasses_json import dataclass_json

from src.nurapy.protocol.command import extract_uint32, extract_int32, extract_uint16


class ReaderChipVersion(Enum):
    AS3992 = 1
    AS3993 = 2


class ModuleType(Enum):
    NUR_05W = 1
    XNUR_05W = 2
    NUR_L2_05W = 3
    NUR_L2_1W = 4


@dataclass_json
@dataclass
class NurDeviceCaps:
    dwSize: int = None
    flagSet1: int = None
    flagSet2: int = None
    maxTxdBm: int = None
    txAttnStep: int = None
    maxTxmW: int = None
    txSteps: int = None
    szTagBuffer: int = None
    curCfgMaxAnt: int = None
    curCfgMaxGPIO: int = None
    chipVersion: ReaderChipVersion = None
    moduleType: ModuleType = None
    moduleConfigFlags: int = None


def parse_get_device_capabilities_response(payload: bytearray):
    device_caps = NurDeviceCaps()
    device_caps.dwSize = extract_uint32(payload)
    device_caps.flagSet1 = extract_uint32(payload)
    device_caps.flagSet2 = extract_uint32(payload)
    device_caps.maxTxdBm = extract_int32(payload)
    device_caps.txAttnStep = extract_int32(payload)
    device_caps.maxTxmW = extract_uint16(payload)
    device_caps.txSteps = extract_uint16(payload)
    device_caps.szTagBuffer = extract_uint16(payload)
    device_caps.curCfgMaxAnt = extract_uint16(payload)
    device_caps.curCfgMaxGPIO = extract_uint16(payload)
    device_caps.chipVersion = ReaderChipVersion(extract_uint16(payload))
    device_caps.moduleType = ModuleType(extract_uint16(payload))
    device_caps.moduleConfigFlags = extract_uint32(payload)
    return device_caps
