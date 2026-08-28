#!/usr/bin/env python3
"""actuator_test.py — покрутити один вихід і коректно відпустити."""
import struct, sys, time
from pymavlink import mavutil

mav = mavutil.mavlink
AUTOPILOT = mav.MAV_COMP_ID_AUTOPILOT1


def param_to_int(m):
    """Ціле в PARAM_VALUE лежить БАЙТАМИ у полі float: борт кладе його memcpy,
    pymavlink віддає те саме поле як число — байти доводиться повертати назад."""
    if m.param_type == mav.MAV_PARAM_TYPE_REAL32:
        return int(round(m.param_value))
    return struct.unpack('<i', struct.pack('<f', m.param_value))[0]


def param_name(m):
    v = m.param_id
    if isinstance(v, (bytes, bytearray)):
        v = v.decode('ascii', 'replace')
    return v.split('\x00', 1)[0]      # поле фіксованої довжини, нуля може не бути


def read_output_functions(link, max_channels=16):
    """Перелік каналів наперед невідомий: питаємо всі можливі,
    лишаємо ті, що відповіли."""
    wanted = ['%s%d' % (bank, ch)
              for bank in ('PWM_MAIN_FUNC', 'PWM_AUX_FUNC')
              for ch in range(1, max_channels + 1)]
    got = {}

    for _ in range(2):
        if len(got) == len(wanted):
            break
        for name in wanted:
            if name not in got:
                link.mav.param_request_read_send(
                    link.target_system, AUTOPILOT, name.encode(), -1)
        deadline = time.monotonic() + 1.5
        while time.monotonic() < deadline and len(got) < len(wanted):
            m = link.recv_match(type='PARAM_VALUE', blocking=True, timeout=0.1)
            if m is None:
                continue
            name = param_name(m)
            if name in wanted:
                got[name] = param_to_int(m)

    return got                        # мовчазні імена просто не існують
