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
    # Embedded-read bytes, only populated when the inventory was running
    # with INVREADCONFIG active (the notification carries PACKET_FLAG_IRDATA).
    user_mem: bytearray = None


def parse_get_id_buffer_meta_response(payload: bytearray,
                                      with_ir_data: bool = False) -> List[NurTagDataMeta]:
    """Parse a NUR id-buffer-meta payload into a list of tag records.

    Wire layout follows `struct NUR_IDBUFFER_ENTRY` from
    nur_nurapi_micro/source/NurProtocol.h and `ParseIdBuffer()` in
    NurMicroApi.c. Each entry begins with a 1-byte blockLen and the
    following blockLen bytes contain the record.

    Without IR data (blockLen - 12 EPC bytes):
        rssi(1) scaledRssi(1) timestamp(2) freq(4) pc(2) channel(1)
        antennaId(1) epc[blockLen - 12]

    With IR data:
        rssi(1) scaledRssi(1) timestamp(2) freq(4) dataLen(1) pc(2)
        channel(1) antennaId(1) epc[blockLen - 13 - dataLen] data[dataLen]

    The `epcLen` field of the host-side struct is computed from
    `blockLen - dataLen` (the firmware never emits it on the wire).
    """
    tag_list: List[NurTagDataMeta] = []
    while len(payload) > 0:
        block_length = extract_uint8(payload)
        if block_length == 0:
            break
        nur_tag_data_meta = NurTagDataMeta()
        nur_tag_data_meta.rssi = extract_int8(payload)
        nur_tag_data_meta.scaled_rssi = extract_int8(payload)
        nur_tag_data_meta.timestamp = extract_uint16(payload)
        nur_tag_data_meta.frequency = extract_uint32(payload)
        if with_ir_data:
            data_len = extract_uint8(payload)
            nur_tag_data_meta.pc = extract_uint16(payload)
            nur_tag_data_meta.channel = extract_uint8(payload)
            nur_tag_data_meta.antenna_id = extract_uint8(payload)
            # blockLen - 12 meta - 1 antenna - dataLen = EPC length
            epc_length_bytes = block_length - 13 - data_len
            if epc_length_bytes < 0:
                epc_length_bytes = 0
            nur_tag_data_meta.epc = bytearray(payload[:epc_length_bytes])
            del payload[:epc_length_bytes]
            nur_tag_data_meta.user_mem = bytearray(payload[:data_len])
            del payload[:data_len]
        else:
            nur_tag_data_meta.pc = extract_uint16(payload)
            nur_tag_data_meta.channel = extract_uint8(payload)
            nur_tag_data_meta.antenna_id = extract_uint8(payload)
            # Block length covers the whole record. With the 12-byte
            # header already consumed, the rest is the EPC.
            epc_length_bytes = block_length - 12
            nur_tag_data_meta.epc = bytearray(payload[:epc_length_bytes])
            del payload[:epc_length_bytes]
        tag_list.append(nur_tag_data_meta)
    return tag_list
