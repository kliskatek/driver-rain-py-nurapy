from dataclasses import dataclass

from dataclasses_json import dataclass_json

from ..._helpers import extract_int16, extract_uint8


@dataclass_json
@dataclass
class InventoryResponse:
    tags_found: int = None
    tags_in_memory: int = None
    rounds: int = None
    collisions: int = None
    current_q: int = None


def parse_inventory_response(payload: bytearray):
    inventory_response = InventoryResponse()
    inventory_response.tags_found = extract_int16(payload)
    inventory_response.tags_in_memory = extract_int16(payload)
    inventory_response.rounds = extract_uint8(payload)
    inventory_response.collisions = extract_int16(payload)
    inventory_response.current_q = extract_uint8(payload)
    return inventory_response
