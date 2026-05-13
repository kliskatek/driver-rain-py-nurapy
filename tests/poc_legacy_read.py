"""Continuous NUR inventory + user-mem read using opcode 0x41.

Enables embedded user-mem read (NUR_CMD_INVENTORYREAD 0x41, bank=USER,
addr=0x100, 6 words) and streams notifications until Ctrl+C, printing
every tag read with its EPC, RSSI, antenna, and the 12-byte user-mem
payload. Useful for verifying tag presence and signal stability.
"""

import logging
import signal
import sys
import time

from nurapy import NurAPY, ModuleSetup, ModuleSetupFlags
from nurapy.protocol.command.inv_read_config import IrBank, IrType
from nurapy.protocol.command.module_setup import (ModuleSetupLinkFreq,
                                                  ModuleSetupRxDec,
                                                  ModuleSetupInvTarget)


PORT = "COM6"
USER_WORD_ADDR = 0x100
USER_WORD_LEN = 6

logging.basicConfig(level=logging.WARNING)


def main():
    reader = NurAPY()
    reader.connect(PORT)

    # Match RfidDemo defaults for continuous re-reads: session=1 + AB target
    # at max power. Session 1 keeps tag flags ~0.5–5s so tags re-respond once
    # the flag decays; the AB sweep alternates targets each round.
    setup = ModuleSetup()
    setup.link_freq = ModuleSetupLinkFreq.BLF_256
    setup.rx_decoding = ModuleSetupRxDec.MILLER_4
    setup.inventory_q = 2
    setup.inventory_session = 1
    setup.inventory_target = ModuleSetupInvTarget.AB
    setup.tx_level = 0
    reader.set_module_setup(setup_flags=[ModuleSetupFlags.LINKFREQ,
                                         ModuleSetupFlags.RXDEC,
                                         ModuleSetupFlags.INVQ,
                                         ModuleSetupFlags.INVSESSION,
                                         ModuleSetupFlags.INVTARGET,
                                         ModuleSetupFlags.TXLEVEL],
                            module_setup=setup)
    print('Module setup: target=AB, q=2, session=1, tx_level=0 (max)')

    stats = {}  # epc -> {'count': int, 'last_user_mem': str, 'last_rssi': int}
    start = time.monotonic()
    total = 0

    def cb(notification, tags):
        nonlocal total
        elapsed = time.monotonic() - start
        for t in tags:
            epc = bytes(t.epc).hex().upper()
            user_mem = bytes(t.user_mem).hex().upper() if t.user_mem else ''
            entry = stats.setdefault(epc, {'count': 0, 'last_um': '', 'last_rssi': 0})
            entry['count'] += 1
            entry['last_um'] = user_mem
            entry['last_rssi'] = t.rssi
            total += 1
            print(f'[{elapsed:6.2f}s] rssi={t.rssi:4d}  ant={t.antenna_id}  '
                  f'EPC={epc}  USER={user_mem}', flush=True)
        if notification and notification.stopped:
            print(f'[{elapsed:6.2f}s] stream stopped — restarting '
                  f'(rounds={notification.rounds}, q={notification.last_q})',
                  flush=True)
            reader.start_inventory_stream()
        reader.clear_notified_tags()

    reader.set_notification_callback(cb)

    print(f'Enabling IR read (USER@0x{USER_WORD_ADDR:X}, {USER_WORD_LEN}w)')
    reader.set_inventory_read_config(active=True,
                                     bank=IrBank.USER,
                                     word_address=USER_WORD_ADDR,
                                     word_length=USER_WORD_LEN,
                                     ir_type=IrType.EPC_AND_DATA)
    print('Starting continuous inventory stream. Ctrl+C to stop.\n')
    reader.start_inventory_stream()

    def on_sigint(*_):
        print('\nStopping…')
        try:
            reader.stop_inventory_stream()
            reader.set_inventory_read_config(active=False)
            reader.disconnect()
        finally:
            print('\nSummary:')
            for epc, e in sorted(stats.items(), key=lambda kv: -kv[1]['count']):
                print(f"  {e['count']:5d}x  rssi={e['last_rssi']:4d}  "
                      f"EPC={epc}  last_user={e['last_um'] or '<none>'}")
            sys.exit(0)

    signal.signal(signal.SIGINT, on_sigint)
    signal.pause() if hasattr(signal, 'pause') else None
    while True:
        time.sleep(1)


if __name__ == '__main__':
    main()
