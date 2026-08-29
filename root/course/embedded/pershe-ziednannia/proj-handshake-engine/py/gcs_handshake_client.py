#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Клієнт первинного рукостискання наземної станції.

    python gcs_handshake_client.py udpin:127.0.0.1:14550
    python gcs_handshake_client.py /dev/ttyUSB0 --baud 57600
"""

import argparse
import sys
import time

from gcs_handshake import (
    HandshakeError,
    MavLink,
    configure_streams,
    download_mission,
    fetch_parameters,
)

ATTEMPTS = 3          # стільки разів пробуємо весь цикл (автопілот міг перезавантажитись)
RETRY_PAUSE = 2.0


def handshake(device: str, baud: int) -> None:
    """Проходить усі чотири кроки; будь-яка невдача — HandshakeError."""
    link = MavLink(device, baud=baud)
    try:
        print(f"[1/4] чекаю HEARTBEAT на {device}...")
        if not link.wait_heartbeat(timeout=10.0):
            raise HandshakeError("жодного HEARTBEAT за 10 с")
        print(f"[OK] апарат SysID={link.target_system} CompID={link.target_component} "
              f"type={link.vehicle_type} autopilot={link.autopilot} "
              f"armed={'так' if link.armed else 'ні'}")

        params = fetch_parameters(link)
        configure_streams(link)
        mission = download_mission(link)

        print("\n" + "=" * 56)
        print(">>> СТАНЦІЯ ГОТОВА: зв'язок узгоджено повністю")
        print(f"    параметрів: {len(params)}, точок місії: {len(mission)}")
        for name in ("SYSID_THISMAV", "FRAME_CLASS", "BATT_CAPACITY", "WPNAV_SPEED"):
            if name in params:
                print(f"    {name} = {params[name]}")
        print("=" * 56)
    finally:
        link.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Рукостискання GCS з автопілотом MAVLink")
    parser.add_argument("device", nargs="?", default="udpin:127.0.0.1:14550",
                        help="udpin:host:port, tcp:host:port або /dev/ttyUSB0")
    parser.add_argument("--baud", type=int, default=57600, help="швидкість послідовного порту")
    args = parser.parse_args()

    for attempt in range(1, ATTEMPTS + 1):
        try:
            handshake(args.device, args.baud)
            return 0
        except HandshakeError as exc:
            print(f"[ERR] спроба {attempt}/{ATTEMPTS}: {exc}")
            if attempt < ATTEMPTS:
                time.sleep(RETRY_PAUSE)
        except KeyboardInterrupt:
            print("\n[GCS] зупинено оператором")
            return 130

    print("[ERR] рукостискання не вдалося")
    return 1


if __name__ == "__main__":
    sys.exit(main())
