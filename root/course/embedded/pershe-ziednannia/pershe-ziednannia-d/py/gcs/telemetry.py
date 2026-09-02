"""Фаза 3: бюджет радіоканалу й індивідуальні інтервали потоків телеметрії."""

from dataclasses import dataclass

from pymavlink import mavutil

mav = mavutil.mavlink

AIR_BYTES_PER_SECOND = 3500.0   # 57600 бод у SiK дають в ефірі ~3.2–3.8 КБ/с корисних
MAX_SHARE = 0.40                # телеметрії — не більше 40% смуги
ACK_TIMEOUT = 0.6
MAX_ATTEMPTS = 3
HEARTBEAT_BYTES_PER_SECOND = 28.0  # борт шле його сам, 1 Гц


@dataclass
class Stream:
    name: str
    msgid: int
    legacy_stream: int   # категорія для відкату на застарілий REQUEST_DATA_STREAM
    hz: float
    frame_bytes: int
    reducible: bool

    @property
    def bytes_per_second(self) -> float:
        return self.hz * self.frame_bytes

    @property
    def interval_us(self) -> int:
        return round(1e6 / self.hz)


def default_plan() -> list[Stream]:
    """Те, без чого польотний інтерфейс не працює. Решту борт нехай не шле взагалі."""
    return [
        Stream("ATTITUDE", mav.MAVLINK_MSG_ID_ATTITUDE,
               mav.MAV_DATA_STREAM_EXTRA1, 20.0, 40, True),
        Stream("GLOBAL_POSITION_INT", mav.MAVLINK_MSG_ID_GLOBAL_POSITION_INT,
               mav.MAV_DATA_STREAM_POSITION, 5.0, 38, True),
        Stream("VFR_HUD", mav.MAVLINK_MSG_ID_VFR_HUD,
               mav.MAV_DATA_STREAM_EXTRA2, 5.0, 30, True),
        Stream("SYS_STATUS", mav.MAVLINK_MSG_ID_SYS_STATUS,
               mav.MAV_DATA_STREAM_EXTENDED_STATUS, 1.0, 41, False),
        Stream("BATTERY_STATUS", mav.MAVLINK_MSG_ID_BATTERY_STATUS,
               mav.MAV_DATA_STREAM_EXTENDED_STATUS, 1.0, 46, False),
        Stream("GPS_RAW_INT", mav.MAVLINK_MSG_ID_GPS_RAW_INT,
               mav.MAV_DATA_STREAM_EXTENDED_STATUS, 2.0, 40, False),
    ]


class TelemetrySetup:
    def __init__(self, link):
        self.link = link
        self.state = "idle"
        self.plan: list[Stream] = []
        self.index = 0
        self.attempts = 0
        self.last_tx = 0.0

    @property
    def done(self) -> bool:
        return self.state == "done"

    def start(self, tsys: int, tcomp: int, supports_set_interval: bool, now: float) -> None:
        self.tsys, self.tcomp = tsys, tcomp
        self.plan = default_plan()
        self.index = 0
        self.attempts = 0
        self._fit_to_budget()
        self._print_budget()

        if not supports_set_interval:
            # Старий борт не вміє #511 — лишається груба нарізка категоріями.
            self._legacy_fallback()
            self.state = "done"
            return
        self.state = "sending"
        self._send_current(now)

    def _fit_to_budget(self) -> None:
        limit = AIR_BYTES_PER_SECOND * MAX_SHARE
        while True:
            total = HEARTBEAT_BYTES_PER_SECOND + sum(s.bytes_per_second for s in self.plan)
            if total <= limit:
                return
            # Ріжемо найдорожчий потік із тих, які взагалі можна різати.
            reducible = [s for s in self.plan if s.reducible and s.hz > 1.0]
            if not reducible:
                print("[!] план телеметрії не вміщується в канал навіть після урізань")
                return
            worst = max(reducible, key=lambda s: s.bytes_per_second)
            worst.hz /= 2.0
            print(f"[3/5] бюджет перевищено: {worst.name} знижено до {worst.hz:g} Гц")

    def _print_budget(self) -> None:
        total = HEARTBEAT_BYTES_PER_SECOND
        packets = 1.0
        print("[3/5] бюджет телеметрії для 57600 бод:")
        for s in self.plan:
            total += s.bytes_per_second
            packets += s.hz
            print(f"      {s.name:<20}{s.hz:>5g} Гц  інтервал {s.interval_us:>8} мкс  "
                  f"{s.bytes_per_second:>6.0f} Б/с")
        free = 100.0 * (1.0 - total / AIR_BYTES_PER_SECOND)
        print(f"      разом {packets:.0f} пак/с, {total:.0f} Б/с — вільно {free:.1f}% каналу")

    def _send_current(self, now: float) -> None:
        s = self.plan[self.index]
        self.link.mav.command_long_send(
            self.tsys, self.tcomp,
            mav.MAV_CMD_SET_MESSAGE_INTERVAL,
            self.attempts,        # confirmation: номер спроби
            float(s.msgid),       # param1: Message ID
            float(s.interval_us),  # param2: інтервал у мікросекундах
            0.0, 0.0, 0.0, 0.0, 0.0,
        )
        self.last_tx = now
        self.attempts += 1

    def on_message(self, msg, now: float) -> None:
        if self.state != "sending" or msg.get_type() != "COMMAND_ACK":
            return
        if msg.command != mav.MAV_CMD_SET_MESSAGE_INTERVAL:
            return  # квитанція на чужу команду

        s = self.plan[self.index]
        if msg.result == mav.MAV_RESULT_ACCEPTED:
            print(f"      {s.name}: ACCEPTED")
        elif msg.result == mav.MAV_RESULT_UNSUPPORTED:
            print(f"[!] {s.name}: борт не підтримує #511 — переходимо на категорії")
            self._legacy_fallback()
            self.state = "done"
            return
        else:
            print(f"[!] {s.name}: відмова, код MAV_RESULT={msg.result}")

        self.index += 1
        if self.index >= len(self.plan):
            self.state = "done"
            print("[3/5] потоки телеметрії налаштовано")
            return
        self.attempts = 0
        self._send_current(now)  # наступну команду — лише після квитанції на попередню

    def tick(self, now: float) -> None:
        if self.state != "sending" or now - self.last_tx < ACK_TIMEOUT:
            return
        if self.attempts >= MAX_ATTEMPTS:
            print(f"[!] {self.plan[self.index].name}: квитанції немає після {MAX_ATTEMPTS} "
                  f"спроб, потік пропущено")
            self.index += 1
            if self.index >= len(self.plan):
                self.state = "done"
                return
            self.attempts = 0
        # Повтор із зростаючим confirmation — борт відрізнить його від нової команди.
        self._send_current(now)

    def _legacy_fallback(self) -> None:
        # REQUEST_DATA_STREAM вмикає цілу категорію, тож для кожної беремо
        # найвищу з потрібних нам частот у ній.
        groups: dict[int, float] = {}
        for s in self.plan:
            groups[s.legacy_stream] = max(groups.get(s.legacy_stream, 0.0), s.hz)
        for stream_id, hz in groups.items():
            self.link.mav.request_data_stream_send(self.tsys, self.tcomp, stream_id, round(hz), 1)
        print(f"[3/5] увімкнено {len(groups)} категорій через REQUEST_DATA_STREAM")
