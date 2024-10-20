from dataclasses import dataclass
from typing import List

from dataclasses_json import dataclass_json

from ..._helpers import extract_uint8, extract_int8, extract_uint16, extract_uint32


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


def parse_get_id_buffer_meta_response(payload: bytearray) -> List[NurTagDataMeta]:
    tag_list: List[NurTagDataMeta] = []
    while len(payload) > 0:
        block_length = extract_int8(payload)
        nur_tag_data_meta = NurTagDataMeta()
        nur_tag_data_meta.rssi = extract_int8(payload)
        nur_tag_data_meta.scaled_rssi = extract_int8(payload)
        nur_tag_data_meta.timestamp = extract_uint16(payload)
        nur_tag_data_meta.frequency = extract_uint32(payload)
        nur_tag_data_meta.pc = extract_uint16(payload)
        nur_tag_data_meta.channel = extract_uint8(payload)
        nur_tag_data_meta.antenna_id = extract_uint8(payload)
        # epc_length_words = (nur_tag_data_meta.pc & 0b1111100000000000) >> 11
        # epc_length_bytes = epc_length_words*2
        epc_length_bytes = block_length - 12
        nur_tag_data_meta.epc = payload[:epc_length_bytes]
        payload = payload[epc_length_bytes:]
        tag_list.append(nur_tag_data_meta)
    return tag_list
