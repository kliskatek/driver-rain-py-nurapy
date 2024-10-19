from dataclasses import dataclass

from dataclasses_json import dataclass_json

from src.nurapy.protocol.command import extract_int16, extract_uint8
from src.nurapy.protocol.command.get_id_buffer_meta import parse_get_id_buffer_meta_response


@dataclass_json
@dataclass
class InventoryStreamNotification:
    stopped: bool = None
    rounds: int = None
    collisions: int = None
    last_q: int = None


def parse_inventory_stream_notification(payload: bytearray):
    inventory_stream_notification = InventoryStreamNotification()
    inventory_stream_notification.stopped = bool(extract_uint8(payload))
    inventory_stream_notification.rounds = extract_uint8(payload)
    inventory_stream_notification.collisions = extract_int16(payload)
    inventory_stream_notification.last_q = extract_uint8(payload)
    tag_data = parse_get_id_buffer_meta_response(payload)
    return [inventory_stream_notification, tag_data]
