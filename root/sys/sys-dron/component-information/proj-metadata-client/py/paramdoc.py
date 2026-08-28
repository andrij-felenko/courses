#!/usr/bin/env python3
"""paramdoc.py — опис одного параметра, витягнутий з борту протоколом метаданих."""
import json, lzma, os, struct, sys, time, zlib
from urllib.request import urlopen
from pymavlink import mavutil

mav       = mavutil.mavlink
AUTOPILOT = mav.MAV_COMP_ID_AUTOPILOT1          # метадані віддає лише автопілот
CACHE_DIR = os.path.join(os.path.expanduser('~'), '.cache', 'compinfo')


def request_message(link, msg_id, msg_name, timeout=5.0):
    """Попросити одне повідомлення. Повертає повідомлення або None."""
    link.mav.command_long_send(
        link.target_system, AUTOPILOT,
        mav.MAV_CMD_REQUEST_MESSAGE, 0,          # confirmation
        msg_id, 0, 0, 0, 0, 0, 0)                # param1 — номер повідомлення

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        # Чекаємо на обидві відповіді разом: порядок між ними не визначений.
        m = link.recv_match(type=[msg_name, 'COMMAND_ACK'],
                            blocking=True, timeout=0.3)
        if m is None:
            continue
        if m.get_type() == msg_name:
            return m
        if m.command == mav.MAV_CMD_REQUEST_MESSAGE and \
           m.result != mav.MAV_RESULT_ACCEPTED:
            return None                          # «не вмію» — досиджувати нема чого
    return None


def cstr(field):
    """char[100] на дроті: хвіст добитий нулями, рядок обривається на першому."""
    if isinstance(field, (bytes, bytearray)):
        field = field.decode('utf-8', 'replace')
    return field.split('\x00', 1)[0].strip()
