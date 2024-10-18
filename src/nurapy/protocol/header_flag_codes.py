from enum import Enum


class HeaderFlagCodes(Enum):
    RESPONSE = 0x0000
    NOTIFICATION = 0x0001
    INVENTORY_READ_NOTIFICATION = 0x0002
