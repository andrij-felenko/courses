"""Клієнт первинного рукостискання: веде апарат через п'ять фаз до робочого стану.

Запуск: python main.py /dev/ttyUSB0 57600
"""

import os
import sys
import time

# Вмикаємо MAVLink 2 до першого імпорту pymavlink: далі бібліотека сама
# відповідає в тому діалекті, який зафіксувала на першому валідному кадрі.
os.environ.setdefault("MAVLINK20", "1")

from gcs.handshake import HandshakeEngine  # noqa: E402
from gcs.link import Link                  # noqa: E402
from gcs.vehicle import monotonic          # noqa: E402


def main() -> int:
    device = sys.argv[1] if len(sys.argv) > 1 else "/dev/ttyUSB0"
    baud = int(sys.argv[2]) if len(sys.argv) > 2 else 57600

    try:
        link = Link(device, baud)
    except OSError as exc:
        print(f"[fatal] не відкрився порт {device}: {exc}")
        return 1

    engine = HandshakeEngine(link)
    print(f"[gcs] слухаємо {device} на {baud} бод; ефір поки мовчимо")

    try:
        while True:
            # Неблокувальний цикл: жодна фаза не має права зупинити вичитку порту,
            # інакше буфер модема переповниться і кадри поб'ються.
            now = monotonic()
            for msg in link.poll():
                engine.on_message(msg, now)
            engine.tick(now)
            time.sleep(0.005)
    except KeyboardInterrupt:
        print(f"\n[gcs] зупинено оператором, стан {engine.state}")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
