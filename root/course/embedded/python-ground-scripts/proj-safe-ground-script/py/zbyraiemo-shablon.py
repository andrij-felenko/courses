#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Переносний каркас наземного скрипта: під'єднатись, вести знімок стану,
крутити подієвий цикл — і при БУДЬ-ЯКОМУ виході лишити апарат у безпеці.
Спершу перевіряй проти SITL (udpin:localhost:14550); на живому борту —
зі знятими гвинтами."""
import time
import signal
from pymavlink import mavutil

CONN = 'udpin:localhost:14550'   # SITL; реальний модем: 'serial:COM5:115200'


class Vehicle:
    """Живий знімок стану апарата — рівно те, що треба для безпечного виходу."""
    def __init__(self):
        self.armed = False
        self.rel_alt_m = 0.0
        self.last_heartbeat = None

    def on_message(self, msg):
        t = msg.get_type()
        if t == 'HEARTBEAT':
            self.last_heartbeat = time.time()
            self.armed = bool(msg.base_mode
                              & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED)
        elif t == 'GLOBAL_POSITION_INT':
            self.rel_alt_m = msg.relative_alt / 1000.0

    def on_ground(self):
        return self.rel_alt_m < 0.5

    def link_alive(self):
        if self.last_heartbeat is None:
            return False
        return (time.time() - self.last_heartbeat) < 3.0


def install_signal_handlers():
    """kill (SIGTERM) → той самий керований вихід, що й Ctrl+C (крізь finally)."""
    def _graceful(signum, frame):
        raise KeyboardInterrupt
    signal.signal(signal.SIGTERM, _graceful)


def cleanup(m, v):
    """Привести апарат у безпеку й закрити лінію — при будь-якому виході."""
    try:
        if m is not None and v.link_alive() and v.armed and v.on_ground():
            print("[EXIT] апарат на землі й озброєний — роззброюю")
            m.mav.command_long_send(
                m.target_system, m.target_component,
                mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
                0, 0, 0, 0, 0, 0, 0, 0)   # param1=0 disarm, param2=0 — звичайний
        else:
            print("[EXIT] у польоті / стан невідомий / лінія мертва — мотори не чіпаю")
    finally:
        if m is not None:
            m.close()
        print("[EXIT] з'єднання закрито")


def main():
    install_signal_handlers()             # ← щоб finally ловив і kill, не лише Ctrl+C
    m = mavutil.mavlink_connection(CONN)
    v = Vehicle()
    m.wait_heartbeat()
    print("апарат на лінії: sys %d, comp %d" % (m.target_system, m.target_component))

    try:
        while True:
            msg = m.recv_match(blocking=True, timeout=1.0)
            if msg is not None:
                v.on_message(msg)

            # ─────────── ТВОЯ ЛОГІКА ТУТ ───────────
            # спираєшся на знімок v: v.armed, v.rel_alt_m, v.on_ground()...
            # разові команди (arm, set_mode, takeoff) шли з підтвердженням і повтором;
            # безперервні уставки — з обмеженою частотою.
            # ────────────────────────────────────────

    except KeyboardInterrupt:
        print("\n[EXIT] Ctrl+C — акуратне завершення")
    finally:
        cleanup(m, v)                     # спрацює хай як ми вийшли з циклу


if __name__ == '__main__':
    main()
