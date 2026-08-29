# -*- coding: utf-8 -*-
"""Крок MISSION_SYNC: транзакційна вичитка польотного плану."""

from pymavlink import mavutil

from .link import HandshakeError

COUNT_TIMEOUT = 3.0
COUNT_ATTEMPTS = 3
ITEM_TIMEOUT = 1.5
ITEM_ATTEMPTS = 4

MISSION = mavutil.mavlink.MAV_MISSION_TYPE_MISSION


def _fetch_count(link) -> int:
    for attempt in range(1, COUNT_ATTEMPTS + 1):
        link.mav.mission_request_list_send(link.target_system, link.target_component, MISSION)
        msg = link.pump(["MISSION_COUNT", "MISSION_ACK"], timeout=COUNT_TIMEOUT)
        if msg is None:
            print(f"  повтор MISSION_REQUEST_LIST (спроба {attempt})")
            continue
        if msg.get_type() == "MISSION_ACK":
            # На запит списку ACK приходить лише як відмова.
            raise HandshakeError(f"апарат відмовив у видачі плану (type={msg.type})")
        if msg.mission_type != MISSION:
            continue  # геозона чи точки повернення — не наша транзакція
        return int(msg.count)
    raise HandshakeError("немає відповіді на MISSION_REQUEST_LIST")


def _fetch_item(link, seq: int):
    for attempt in range(1, ITEM_ATTEMPTS + 1):
        link.mav.mission_request_int_send(
            link.target_system, link.target_component, seq, MISSION
        )
        item = link.pump(["MISSION_ITEM_INT"], timeout=ITEM_TIMEOUT)
        if item is not None and item.seq == seq:
            return item
        # спізніла відповідь на попередній повтор або тиша — питаємо ще раз
        print(f"    [WARN] повтор запиту точки #{seq} (спроба {attempt})")
    raise HandshakeError(f"точка місії #{seq} не приходить")


def download_mission(link) -> list:
    print("\n[4/4] MISSION_REQUEST_LIST — забираю польотний план...")
    total = _fetch_count(link)
    print(f"  точок на борту: {total}")

    items = []
    for seq in range(total):
        item = _fetch_item(link, seq)
        items.append(item)
        print(f"    #{seq}: cmd={item.command} lat={item.x / 1e7:.7f} "
              f"lon={item.y / 1e7:.7f} alt={item.z:.1f} м")

    # MISSION_ACK закриває транзакцію навіть для порожнього плану — без нього
    # автопілот вважає вичитку незавершеною й блокує наступні операції.
    link.mav.mission_ack_send(
        link.target_system, link.target_component,
        mavutil.mavlink.MAV_MISSION_ACCEPTED, MISSION,
    )
    print("[OK] план вичитано й підтверджено" if total else "[OK] план порожній, ACK відправлено")
    return items
