# -*- coding: utf-8 -*-
"""Канал до апарата: неблокувальна вичитка й власне серцебиття станції."""

import time

from pymavlink import mavutil

GCS_SYSTEM = 255
GCS_COMPONENT = 190
HEARTBEAT_PERIOD = 1.0
POLL_SLEEP = 0.01


class HandshakeError(RuntimeError):
    """Крок рукостискання не пройшов — верхній рівень вирішує, чи повторювати."""


class MavLink:
    def __init__(self, device: str, baud: int = 57600):
        self.master = mavutil.mavlink_connection(
            device,
            baud=baud,
            source_system=GCS_SYSTEM,
            source_component=GCS_COMPONENT,
        )
        self.target_system = 0
        self.target_component = 0
        self.vehicle_type = None
        self.autopilot = None
        self.armed = False
        self._last_beat = 0.0

    @property
    def mav(self):
        """Кодувальник кадрів: link.mav.param_request_list_send(...) тощо."""
        return self.master.mav

    def close(self) -> None:
        self.master.close()

    def pump(self, types, timeout: float = 0.0):
        """Крутить канал не довше timeout і повертає перше повідомлення з types.

        Блокувального recv тут немає навмисно: втрачений пакет не має
        зупиняти станцію, а годинник таймаутів мусить іти далі.
        """
        deadline = time.monotonic() + timeout
        while True:
            self._beat()
            msg = self.master.recv_match(type=types, blocking=False)
            if msg is not None:
                kind = msg.get_type()
                if kind == "BAD_DATA":
                    continue  # побитий кадр: CRC не зійшлася
                if self.target_system and msg.get_srcSystem() != self.target_system:
                    continue  # чужий апарат у спільному ефірі
                return msg
            if time.monotonic() >= deadline:
                return None
            time.sleep(POLL_SLEEP)

    def wait_heartbeat(self, timeout: float = 10.0) -> bool:
        """Пасивно слухає ефір: до першого серцебиття станція нічого не питає."""
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            msg = self.pump(["HEARTBEAT"], timeout=0.2)
            if msg is None:
                continue
            if msg.get_srcSystem() == self.master.source_system:
                continue  # власне відлуння
            if msg.type == mavutil.mavlink.MAV_TYPE_GCS:
                continue  # сусідня станція
            if msg.get_srcComponent() != mavutil.mavlink.MAV_COMP_ID_AUTOPILOT1:
                continue  # компаньйон чи камера, а не автопілот

            self.target_system = msg.get_srcSystem()
            self.target_component = msg.get_srcComponent()
            self.vehicle_type = msg.type
            self.autopilot = msg.autopilot
            self.armed = bool(msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED)
            # pymavlink підставляє ці ж цілі у свої зручні виклики
            self.master.target_system = self.target_system
            self.master.target_component = self.target_component
            return True
        return False

    def _beat(self) -> None:
        """Серцебиття станції раз на секунду: без нього спрацює GCS-failsafe."""
        now = time.monotonic()
        if now - self._last_beat < HEARTBEAT_PERIOD:
            return
        self._last_beat = now
        self.master.mav.heartbeat_send(
            mavutil.mavlink.MAV_TYPE_GCS,
            mavutil.mavlink.MAV_AUTOPILOT_INVALID,
            0, 0,
            mavutil.mavlink.MAV_STATE_ACTIVE,
        )
