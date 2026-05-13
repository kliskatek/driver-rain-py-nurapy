"""NUR_CMD_INVREADCONFIG (0x23) — configure embedded Read for subsequent
inventories. Mirrors `struct NUR_CMD_IRCONFIG_PARAMS` in nur_nurapi_micro
(NurProtocol.h ~line 422):

    uint8_t  active     1 = enable, 0 = disable (when disabling, send only this byte)
    uint8_t  type       0 = EPC + read data, 1 = read data only (placed in EPC field)
    uint8_t  bank       0=reserved, 1=epc, 2=tid, 3=user
    uint32_t wAddress   word address (LE)
    uint8_t  wLength    word count (1 word = 16 bits)
"""

from enum import IntEnum

from ..._helpers import to_uint8_bytes, to_uint32_bytes


class IrBank(IntEnum):
    RESERVED = 0
    EPC = 1
    TID = 2
    USER = 3


class IrType(IntEnum):
    EPC_AND_DATA = 0   # EPC plus read data
    DATA_ONLY = 1      # only read data, returned in the EPC field


def build_inv_read_config_payload(active: bool,
                                  bank: IrBank = IrBank.USER,
                                  w_address: int = 0,
                                  w_length: int = 0,
                                  ir_type: IrType = IrType.EPC_AND_DATA) -> bytearray:
    if not active:
        return bytearray(to_uint8_bytes(0))
    payload = bytearray()
    payload += to_uint8_bytes(1)
    payload += to_uint8_bytes(int(ir_type))
    payload += to_uint8_bytes(int(bank))
    payload += to_uint32_bytes(int(w_address))
    payload += to_uint8_bytes(int(w_length))
    return payload
