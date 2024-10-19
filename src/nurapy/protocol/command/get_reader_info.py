from dataclasses import dataclass

from dataclasses_json import dataclass_json

from src.nurapy.protocol.command._helpers import extract_bytes, extract_string, extract_uint8


@dataclass_json
@dataclass
class NurReaderInfo:
    serial: str = None
    alt_serial: str = None
    name: str = None
    fcc_id: str = None
    hw_version: str = None
    sw_version: str = None
    dev_build: int = None
    num_gpio: int = None
    num_sensors: int = None
    num_regions: int = None
    num_antennas: int = None
    max_antennas: int = None


def extract_sw_version(payload: bytearray) -> str:
    major = str(payload[0])
    minor = str(payload[1])
    build = chr(payload[2])
    del payload[:4]
    return major + '.' + minor + '.' + build


def parse_get_reader_info_response(payload: bytearray):
    reader_info = NurReaderInfo()
    unknown = extract_bytes(payload, 4)
    reader_info.serial = extract_string(payload)
    reader_info.alt_serial = extract_string(payload)
    reader_info.name = extract_string(payload)
    reader_info.fcc_id = extract_string(payload)
    reader_info.hw_version = extract_string(payload)
    reader_info.sw_version = extract_sw_version(payload)
    reader_info.num_sensors = extract_uint8(payload)
    reader_info.num_regions = extract_uint8(payload)
    reader_info.num_antennas = extract_uint8(payload)
    reader_info.max_antennas = extract_uint8(payload)
    return reader_info
