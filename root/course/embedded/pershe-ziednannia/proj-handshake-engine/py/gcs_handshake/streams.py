# -*- coding: utf-8 -*-
"""Крок STREAM_CONFIG: замовлення частот телеметрії з перевіркою COMMAND_ACK."""

import time

from pymavlink import mavutil

ACK_TIMEOUT = 0.7
ATTEMPTS = 4

STREAMS = [
    (mavutil.mavlink.MAVLINK_MSG_ID_ATTITUDE, 50000, "ATTITUDE 20 Гц"),
    (mavutil.mavlink.MAVLINK_MSG_ID_GLOBAL_POSITION_INT, 200000, "GLOBAL_POSITION_INT 5 Гц"),
    (mavutil.mavlink.MAVLINK_MSG_ID_SYS_STATUS, 1000000, "SYS_STATUS 1 Гц"),
    (mavutil.mavlink.MAVLINK_MSG_ID_BATTERY_STATUS, 1000000, "BATTERY_STATUS 1 Гц"),
]


def _set_interval(link, msg_id: int, interval_us: int) -> bool:
    command = mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL
    for attempt in range(ATTEMPTS):
        link.mav.command_long_send(
            link.target_system, link.target_component,
            command,
            attempt,                 # поле confirmation зростає з повторами
            float(msg_id), float(interval_us),
            0, 0, 0, 0, 0,
        )
        deadline = time.monotonic() + ACK_TIMEOUT
        while time.monotonic() < deadline:
            ack = link.pump(["COMMAND_ACK"], timeout=0.05)
            if ack is None or ack.command != command:
                continue
            if ack.result == mavutil.mavlink.MAV_RESULT_ACCEPTED:
                return True
            if ack.result == mavutil.mavlink.MAV_RESULT_IN_PROGRESS:
                deadline = time.monotonic() + ACK_TIMEOUT  # прошивка взялася
                continue
            if ack.result in (mavutil.mavlink.MAV_RESULT_UNSUPPORTED,
                              mavutil.mavlink.MAV_RESULT_DENIED):
                print(f"  [WARN] прошивка не приймає команду (result={ack.result})")
                return False
            break  # тимчасова відмова — нова спроба з новим confirmation
    return False


def configure_streams(link) -> None:
    print("\n[3/4] MAV_CMD_SET_MESSAGE_INTERVAL — замовляю частоти телеметрії...")
    for msg_id, interval_us, label in STREAMS:
        if _set_interval(link, msg_id, interval_us):
            print(f"  {label}: ACK")
        else:
            # Телеметрія — не привід валити рукостискання: старі прошивки
            # просто мовчать, лишаючи потоки на типових частотах.
            print(f"  [WARN] {label}: підтвердження немає, іду далі")
    print("[OK] потоки телеметрії налаштовано")
