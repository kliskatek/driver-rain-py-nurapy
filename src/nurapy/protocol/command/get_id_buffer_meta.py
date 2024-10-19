from dataclasses import dataclass

from dataclasses_json import dataclass_json

from src.nurapy.protocol.command import extract_uint8, extract_int8, extract_uint16, extract_uint32


@dataclass_json
@dataclass
class NurTagDataMeta:
    rssi: int = None
    scaled_rssi: int = None
    timestamp: int = None
    frequency: float = None
    pc: bytearray = None
    channel: int = None
    antenna_id: int = None
    epc: bytearray = None


def parse_get_id_buffer_meta_response(payload: bytearray) -> bytearray:
    block_length = extract_int8(payload)
    nur_tag_data_meta = NurTagDataMeta()
    nur_tag_data_meta.rssi = extract_int8(payload)
    nur_tag_data_meta.scaled_rssi = extract_int8(payload)
    nur_tag_data_meta.timestamp = extract_uint16(payload)
    nur_tag_data_meta.frequency = extract_uint32(payload)
    nur_tag_data_meta.pc = extract_uint16(payload)
    nur_tag_data_meta.channel = extract_uint8(payload)
    nur_tag_data_meta.antenna_id = extract_uint8(payload)
    nur_tag_data_meta.epc = payload
    return nur_tag_data_meta
