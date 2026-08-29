#!/usr/bin/env python3
"""Тестовий генератор вимірів: вузол без заліза.

Робить те саме, що прошивка з тек `c/` і `cpp/`, але коротко й на Python —
щоб перевірити весь ланцюг, не збираючи жодного бінарника. Додатково
навмисно псує потік сміттєвими байтами: кадрувальник шлюзу мусить
відновитися сам, і в його підсумковому рядку це видно числом.

Запуск:  python node_sim.py [node_id] [host] [port]
"""

from __future__ import annotations

import random
import socket
import sys
import time

from gateway import protocol as proto
from gateway.framer import StreamFramer

PERIOD_S = 2.0
GARBAGE_EVERY = 5   # раз на стільки вимірів підмішуємо сміття в потік


def handle_command(sock: socket.socket, node_id: int, cmd: proto.Command,
                   state: dict) -> None:
    """Виконує команду й відповідає квитанцією — без неї шлюз повторюватиме."""
    if cmd.node_id != node_id:
        return

    status = proto.ACK_UNKNOWN_CMD
    if cmd.cmd_id == proto.CMD_SET_RELAY:
        if cmd.value <= 1:
            state["relay_on"] = bool(cmd.value)
            status = proto.ACK_OK
        else:
            status = proto.ACK_BAD_VALUE

    flags = proto.FLAG_RELAY_ON if state["relay_on"] else 0
    sock.sendall(proto.encode_ack(node_id, cmd.seq, cmd.cmd_id, status, flags))
    print(f"[sim {node_id}] команда seq={cmd.seq} → status={status}, "
          f"реле={'увімкнено' if state['relay_on'] else 'вимкнено'}")


def main() -> int:
    node_id = int(sys.argv[1]) if len(sys.argv) > 1 else 42
    host = sys.argv[2] if len(sys.argv) > 2 else "127.0.0.1"
    port = int(sys.argv[3]) if len(sys.argv) > 3 else 9000

    state = {"relay_on": False}
    temp_c = 23.40
    battery_mv = 3300
    framer = StreamFramer()

    try:
        sock = socket.create_connection((host, port), timeout=5.0)
    except OSError as exc:
        print(f"[sim {node_id}] шлюз {host}:{port} недосяжний — {exc}")
        return 1

    print(f"[sim {node_id}] під'єднано до {host}:{port}")
    sock.settimeout(0.2)

    seq = 0
    next_tx = time.monotonic()
    try:
        while True:
            # Читаємо зворотний канал: команди приходять асинхронно.
            try:
                chunk = sock.recv(256)
                if not chunk:
                    print(f"[sim {node_id}] шлюз закрив з'єднання")
                    return 0
                for raw in framer.feed(chunk):
                    frame = proto.decode(raw)
                    if isinstance(frame, proto.Command):
                        handle_command(sock, node_id, frame, state)
            except socket.timeout:
                pass
            except proto.FrameError as exc:
                print(f"[sim {node_id}] кадр зі шлюзу відкинуто — {exc}")

            if time.monotonic() < next_tx:
                continue
            next_tx += PERIOD_S

            seq += 1
            temp_c = min(35.0, max(10.0, temp_c + random.uniform(-0.2, 0.2)))
            battery_mv = max(3000, battery_mv - random.randint(0, 1))

            if seq % GARBAGE_EVERY == 0:
                # П'ять байтів шуму, серед них фальшива магія 0xAA: рівно та
                # ситуація, заради якої шлюз судить кадр за CRC, а не за 0xAA.
                sock.sendall(bytes([0x00, 0xAA, 0x17, 0xFF, 0x5C]))
                print(f"[sim {node_id}] у потік підмішано 5 сміттєвих байтів")

            frame = proto.encode_telemetry(
                node_id=node_id,
                seq=seq,
                temp_c=temp_c,
                battery_mv=battery_mv,
                relay_on=state["relay_on"],
            )
            sock.sendall(frame)
            print(f"[sim {node_id}] seq={seq}  {temp_c:.2f} °C  {battery_mv} мВ")
    except KeyboardInterrupt:
        print(f"\n[sim {node_id}] зупинка")
        return 0
    except OSError as exc:
        print(f"[sim {node_id}] канал упав — {exc}")
        return 1
    finally:
        sock.close()


if __name__ == "__main__":
    raise SystemExit(main())
