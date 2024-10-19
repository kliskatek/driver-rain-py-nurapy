
def parse_get_id_buffer_response(payload: bytearray) -> bytearray:
    return payload[1:]
