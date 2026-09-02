"""Транспорт: з'єднання pymavlink плюс облік якості радіолінка за лічильником seq."""

from dataclasses import dataclass, field

from pymavlink import mavutil

GCS_SYSTEM_ID = 255
GCS_COMPONENT_ID = mavutil.mavlink.MAV_COMP_ID_MISSIONPLANNER


@dataclass
class LinkStats:
    received: int = 0        # валідних кадрів зібрано
    lost: int = 0            # дірок у нумерації seq
    parse_errors: int = 0    # BAD_DATA: биті CRC і сміття з ефіру

    @property
    def loss_percent(self) -> float:
        total = self.received + self.lost
        return 100.0 * self.lost / total if total else 0.0

    def reset_window(self) -> None:
        self.received = 0
        self.lost = 0


@dataclass
class Link:
    device: str
    baud: int = 57600
    stats: LinkStats = field(default_factory=LinkStats)

    def __post_init__(self) -> None:
        self.master = mavutil.mavlink_connection(
            self.device,
            baud=self.baud,
            source_system=GCS_SYSTEM_ID,
            source_component=GCS_COMPONENT_ID,
        )
        self._last_seq: dict[tuple[int, int], int] = {}
        self.version = self.master.WIRE_PROTOCOL_VERSION

    def poll(self, budget: int = 64):
        """Забирає готові кадри, не блокуючи цикл. Порожній список — норма."""
        msgs = []
        while len(msgs) < budget:
            msg = self.master.recv_match(blocking=False)
            if msg is None:
                break
            if msg.get_type() == "BAD_DATA":
                self.stats.parse_errors += 1
                continue
            self._track_seq(msg)
            msgs.append(msg)
        return msgs

    def _track_seq(self, msg) -> None:
        key = (msg.get_srcSystem(), msg.get_srcComponent())
        self.stats.received += 1
        previous = self._last_seq.get(key)
        seq = msg.get_seq()
        if previous is not None:
            # Втрачені = (seq - попередній - 1) mod 256.
            self.stats.lost += (seq - previous - 1) % 256
        self._last_seq[key] = seq

    def note_protocol(self, heartbeat) -> None:
        """Поле mavlink_version у HEARTBEAT каже, чи борт узагалі знає v2."""
        if heartbeat.mavlink_version >= 3 and self.version != "2.0":
            print("[link] борт підтримує MAVLink 2, але з'єднання відкрито як v1")
        elif heartbeat.mavlink_version < 3:
            print("[link] борт говорить лише MAVLink 1 — відповідаємо в діалекті v1")

    @property
    def mav(self):
        return self.master.mav
