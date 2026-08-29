# -*- coding: utf-8 -*-
"""Крок PARAM_SYNC: повна таблиця параметрів із дозапитом дірок."""

import time

from .link import HandshakeError

QUIET_GAP = 0.8        # пауза в потоці PARAM_VALUE, після якої шукаємо дірки
BATCH = 5              # скільки індексів дозапитуємо однією пачкою
LIST_RETRIES = 5
STALL_TIMEOUT = 20.0   # стільки без жодного НОВОГО параметра — і здаємось


def _decode_name(raw) -> str:
    """ASCII-ідентифікатор із кадру: байти Python 3 і хвіст із \\x00."""
    if isinstance(raw, bytes):
        raw = raw.decode("ascii", errors="ignore")
    return raw.rstrip("\x00").strip()


def _request_holes(link, mask, cursor):
    """Шле до BATCH адресних PARAM_REQUEST_READ, ідучи по масці по колу."""
    size = len(mask)
    sent = 0
    scanned = 0
    while sent < BATCH and scanned < size:
        index = cursor % size
        cursor += 1
        scanned += 1
        if mask[index]:
            continue
        # порожнє ім'я + індекс = читання саме за індексом
        link.mav.param_request_read_send(
            link.target_system, link.target_component, b"", index
        )
        sent += 1
    return cursor % size if size else 0, sent


def fetch_parameters(link) -> dict:
    print("\n[2/4] PARAM_REQUEST_LIST — прошу таблицю параметрів...")
    link.mav.param_request_list_send(link.target_system, link.target_component)

    values = {}
    mask = []
    total = None
    have = 0
    cursor = 0
    list_retries = 0
    last_rx = time.monotonic()
    last_progress = last_rx

    while True:
        msg = link.pump(["PARAM_VALUE"], timeout=0.05)
        if msg is not None:
            last_rx = time.monotonic()
            if total is None and msg.param_count > 0:
                total = int(msg.param_count)
                mask = [False] * total
                print(f"  апарат оголосив {total} параметрів")

            values[_decode_name(msg.param_id)] = msg.param_value

            index = int(msg.param_index)
            # на читання за іменем прошивка відповідає індексом 0xFFFF —
            # значення таке дає, а дірку в масці не закриває
            if total is not None and 0 <= index < total and not mask[index]:
                mask[index] = True
                have += 1
                last_progress = last_rx

            if total is not None and have == total:
                print(f"[OK] усі {total} параметрів на місці")
                return values
            continue

        now = time.monotonic()
        if now - last_progress > STALL_TIMEOUT:
            raise HandshakeError(f"таймаут параметрів: маємо {have} з {total}")
        if now - last_rx < QUIET_GAP:
            continue

        if total is None:
            list_retries += 1
            if list_retries > LIST_RETRIES:
                raise HandshakeError("апарат не відповідає на PARAM_REQUEST_LIST")
            print(f"  повтор PARAM_REQUEST_LIST (спроба {list_retries})")
            link.mav.param_request_list_send(link.target_system, link.target_component)
            last_rx = time.monotonic()
            continue

        cursor, sent = _request_holes(link, mask, cursor)
        print(f"  дозапит дірок: {sent} PARAM_REQUEST_READ, бракує {total - have} з {total}")
        last_rx = time.monotonic()
