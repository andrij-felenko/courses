"""Фаза 1: розбір HEARTBEAT, облік компонентів шини й сторожовий таймер зв'язку."""

import time
from dataclasses import dataclass, field

from pymavlink import mavutil

mav = mavutil.mavlink

HEARTBEAT_TIMEOUT = 3.5  # три пропущені серцебиття поспіль при частоті 1 Гц

VEHICLE_TYPES = {
    mav.MAV_TYPE_FIXED_WING: "літак",
    mav.MAV_TYPE_QUADROTOR: "квадрокоптер",
    mav.MAV_TYPE_HEXAROTOR: "гексакоптер",
    mav.MAV_TYPE_OCTOROTOR: "октокоптер",
    mav.MAV_TYPE_GROUND_ROVER: "наземний ровер",
}
AUTOPILOTS = {
    mav.MAV_AUTOPILOT_ARDUPILOTMEGA: "ArduPilot",
    mav.MAV_AUTOPILOT_PX4: "PX4",
    mav.MAV_AUTOPILOT_INVALID: "не автопілот",
}
STATES = {
    mav.MAV_STATE_BOOT: "завантаження",
    mav.MAV_STATE_CALIBRATING: "калібрування сенсорів",
    mav.MAV_STATE_STANDBY: "очікування зльоту",
    mav.MAV_STATE_ACTIVE: "у польоті",
    mav.MAV_STATE_CRITICAL: "КРИТИЧНИЙ СТАН",
    mav.MAV_STATE_EMERGENCY: "АВАРІЯ",
}
ROLES = {
    mav.MAV_COMP_ID_AUTOPILOT1: "польотний контролер",
    154: "підвіс камери",
    191: "бортовий комп'ютер",
    160: "трекер антени",
}
CAPABILITY_BITS = (
    (mav.MAV_PROTOCOL_CAPABILITY_MISSION_INT, "цілочислові координати місії"),
    (mav.MAV_PROTOCOL_CAPABILITY_PARAM_UNION, "коректні типи параметрів"),
    (mav.MAV_PROTOCOL_CAPABILITY_SET_MESSAGE_INTERVAL, "індивідуальні інтервали потоків (#511)"),
    (mav.MAV_PROTOCOL_CAPABILITY_COMPASS_CALIBRATION, "бортове калібрування магнітометра"),
)


@dataclass
class Component:
    sysid: int
    compid: int
    type: int = 0
    autopilot: int = 0
    base_mode: int = 0
    system_status: int = 0
    custom_mode: int = 0
    capabilities: int = 0
    last_seen: float = 0.0
    alive: bool = True

    @property
    def armed(self) -> bool:
        return bool(self.base_mode & mav.MAV_MODE_FLAG_SAFETY_ARMED)

    @property
    def is_autopilot(self) -> bool:
        return self.compid == mav.MAV_COMP_ID_AUTOPILOT1


@dataclass
class VehicleRegistry:
    components: dict[tuple[int, int], Component] = field(default_factory=dict)

    def on_heartbeat(self, msg, now: float) -> bool:
        """Повертає True, якщо серцебиття надіслав головний автопілот."""
        sysid, compid = msg.get_srcSystem(), msg.get_srcComponent()
        if sysid == 255:  # луна власного серцебиття станції
            return False

        key = (sysid, compid)
        comp = self.components.get(key)
        is_new = comp is None
        if is_new:
            comp = Component(sysid=sysid, compid=compid)
            self.components[key] = comp

        was_silent = not is_new and not comp.alive
        armed_before = comp.armed

        comp.type = msg.type
        comp.autopilot = msg.autopilot
        comp.base_mode = msg.base_mode
        comp.system_status = msg.system_status
        comp.custom_mode = msg.custom_mode
        comp.last_seen = now
        comp.alive = True

        if is_new:
            print(f"[1/5] HEARTBEAT: SysID={sysid} CompID={compid} "
                  f"({ROLES.get(compid, 'інший вузол шини')})")
            if comp.is_autopilot:
                print(f"      платформа: {VEHICLE_TYPES.get(comp.type, 'невідома платформа')}, "
                      f"стек: {AUTOPILOTS.get(comp.autopilot, 'інший стек')}, "
                      f"стан: {STATES.get(comp.system_status, 'невизначений')}, "
                      f"мотори: {'ARMED' if comp.armed else 'DISARMED'}")
        elif was_silent:
            print(f"[link] SysID={sysid} CompID={compid} знову в ефірі")
        elif armed_before != comp.armed:
            # Біт 7 base_mode — єдине джерело правди про напругу на регуляторах.
            print(f"[!] SysID={sysid}: мотори {'ARMED' if comp.armed else 'DISARMED'}")

        return comp.is_autopilot

    def on_autopilot_version(self, msg) -> None:
        comp = self.components.get((msg.get_srcSystem(), msg.get_srcComponent()))
        if comp is None:
            return
        comp.capabilities = msg.capabilities
        print(f"[1/5] AUTOPILOT_VERSION: маска можливостей 0x{msg.capabilities:x}")
        for bit, text in CAPABILITY_BITS:
            print(f"      {'+' if msg.capabilities & bit else '-'} {text}")

    def tick(self, now: float) -> bool:
        """Позначає замовклі вузли; True — головний автопілот мовчить понад 3.5 с."""
        autopilot_silent = False
        for comp in self.components.values():
            if comp.alive and now - comp.last_seen > HEARTBEAT_TIMEOUT:
                comp.alive = False
                print(f"[!] LINK_LOST: SysID={comp.sysid} CompID={comp.compid} мовчить понад 3.5 с")
            if comp.is_autopilot and not comp.alive:
                autopilot_silent = True
        return autopilot_silent

    @property
    def autopilot(self) -> Component | None:
        for key in sorted(self.components):
            comp = self.components[key]
            if comp.is_autopilot:
                return comp
        return None

    def supports(self, capability_bit: int) -> bool:
        comp = self.autopilot
        return comp is not None and bool(comp.capabilities & capability_bit)


def monotonic() -> float:
    return time.monotonic()
