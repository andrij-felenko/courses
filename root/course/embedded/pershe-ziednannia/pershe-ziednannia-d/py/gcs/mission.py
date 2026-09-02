"""Фаза 4: транзакційна вичитка польотного завдання з борту."""

from dataclasses import dataclass

from pymavlink import mavutil

mav = mavutil.mavlink

ITEM_TIMEOUT = 1.5
MAX_RETRIES = 5

FRAMES = {
    mav.MAV_FRAME_GLOBAL: "AMSL",
    mav.MAV_FRAME_GLOBAL_RELATIVE_ALT: "від точки зльоту",
    mav.MAV_FRAME_GLOBAL_TERRAIN_ALT: "над рельєфом",
}
NAV_COMMANDS = {
    mav.MAV_CMD_NAV_WAYPOINT: "WAYPOINT",
    mav.MAV_CMD_NAV_TAKEOFF: "TAKEOFF",
    mav.MAV_CMD_NAV_LAND: "LAND",
    mav.MAV_CMD_NAV_RETURN_TO_LAUNCH: "RTL",
    mav.MAV_CMD_NAV_LOITER_TIME: "LOITER",
}


@dataclass
class MissionItem:
    seq: int
    command: int
    frame: int
    lat_deg: float   # з int32 × 1e-7 — дискретність 1.1 см
    lon_deg: float
    alt_m: float
    hold_s: float
    accept_radius_m: float


class MissionSync:
    def __init__(self, link):
        self.link = link
        self.state = "idle"
        self.items: list[MissionItem] = []
        self.count = 0
        self.expected = 0
        self.retries = 0
        self.pacing = 0.0
        self.last_tx = 0.0

    @property
    def done(self) -> bool:
        return self.state == "done"

    @property
    def failed(self) -> bool:
        return self.state == "failed"

    def start(self, tsys: int, tcomp: int, now: float) -> None:
        self.tsys, self.tcomp = tsys, tcomp
        self.items = []
        self.count = 0
        self.expected = 0
        self.retries = 0
        self.state = "wait_count"
        self._send_request_list(now)

    def _send_request_list(self, now: float) -> None:
        self.link.mav.mission_request_list_send(self.tsys, self.tcomp,
                                                mav.MAV_MISSION_TYPE_MISSION)
        self.last_tx = now
        print("[4/5] MISSION_REQUEST_LIST → скільки точок на борту?")

    def _send_request_item(self, now: float) -> None:
        self.link.mav.mission_request_int_send(self.tsys, self.tcomp, self.expected,
                                               mav.MAV_MISSION_TYPE_MISSION)
        self.last_tx = now

    def _send_ack(self, ack_type: int) -> None:
        self.link.mav.mission_ack_send(self.tsys, self.tcomp, ack_type,
                                       mav.MAV_MISSION_TYPE_MISSION)

    def on_message(self, msg, now: float) -> None:
        if (msg.get_srcSystem(), msg.get_srcComponent()) != (self.tsys, self.tcomp):
            return
        kind = msg.get_type()

        if self.state == "wait_count" and kind == "MISSION_COUNT":
            if msg.mission_type != mav.MAV_MISSION_TYPE_MISSION:
                return  # геозона або rally-точки — не наш план
            self.count = msg.count
            print(f"[4/5] MISSION_COUNT = {self.count}")
            if self.count == 0:
                self._send_ack(mav.MAV_MISSION_ACCEPTED)  # порожній план теж треба закрити
                self.state = "done"
                return
            self.state = "wait_item"
            self.expected = 0
            self.retries = 0
            self._send_request_item(now)
            return

        if self.state == "wait_item" and kind == "MISSION_ITEM_INT":
            # Автопілот міг відповісти із запізненням на попередній запит:
            # чужий номер ігноруємо й далі чекаємо свій.
            if msg.seq != self.expected:
                return
            item = MissionItem(
                seq=msg.seq,
                command=msg.command,
                frame=msg.frame,
                lat_deg=msg.x * 1e-7,
                lon_deg=msg.y * 1e-7,
                alt_m=msg.z,
                hold_s=msg.param1,
                accept_radius_m=msg.param2,
            )
            self.items.append(item)
            print(f"      #{item.seq:>2} {NAV_COMMANDS.get(item.command, 'інша команда')} "
                  f"{item.lat_deg:.7f}, {item.lon_deg:.7f}  h={item.alt_m:.1f} м "
                  f"({FRAMES.get(item.frame, 'інша система відліку')})")

            self.retries = 0
            self.expected += 1
            if self.expected >= self.count:
                self._send_ack(mav.MAV_MISSION_ACCEPTED)  # транзакцію закрито
                self.state = "done"
                print("[4/5] місію вичитано повністю, надіслано MISSION_ACK")
                return
            self.last_tx = now - self.pacing  # пауза на розворот ефіру

    def tick(self, now: float) -> None:
        if self.state not in ("wait_count", "wait_item"):
            return
        if now - self.last_tx < ITEM_TIMEOUT:
            return
        if self.retries >= MAX_RETRIES:
            print(f"[!] точка #{self.expected} не прийшла за {MAX_RETRIES} спроб — "
                  f"транзакцію скасовано")
            self._send_ack(mav.MAV_MISSION_ERROR)
            self.state = "failed"
            return
        self.retries += 1
        if self.state == "wait_count":
            self._send_request_list(now)
        else:
            self._send_request_item(now)
