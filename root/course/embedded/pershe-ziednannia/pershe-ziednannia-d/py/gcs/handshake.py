"""Фаза 5: кінцевий автомат, що зшиває всі фази в один неблокувальний рушій."""

from pymavlink import mavutil

from .mission import MissionSync
from .params import ParamSync
from .telemetry import TelemetrySetup
from .vehicle import VehicleRegistry

mav = mavutil.mavlink

CAPS_TIMEOUT = 1.0
CAPS_ATTEMPTS = 3
PACING_PERIOD = 5.0


class HandshakeEngine:
    def __init__(self, link):
        self.link = link
        self.registry = VehicleRegistry()
        self.params = ParamSync(link)
        self.telemetry = TelemetrySetup(link)
        self.mission = MissionSync(link)

        self.state = "WAIT_HEARTBEAT"
        self.resume = "WAIT_HEARTBEAT"
        self.tsys = self.tcomp = 0
        self.caps_attempts = 0
        self.caps_tx = 0.0
        self.last_gcs_hb = 0.0
        self.last_pacing = 0.0
        self.last_hud = 0.0

    def _enter(self, state: str) -> None:
        if state == self.state:
            return
        print(f"[fsm] {self.state} → {state}")
        self.state = state

    def on_message(self, msg, now: float) -> None:
        kind = msg.get_type()

        # Серцебиття слухаємо в БУДЬ-якому стані: воно годує сторожовий таймер
        # і виявляє нові компоненти шини (підвіс, бортовий комп'ютер).
        if kind == "HEARTBEAT":
            from_autopilot = self.registry.on_heartbeat(msg, now)
            if from_autopilot and self.state == "WAIT_HEARTBEAT":
                self.link.note_protocol(msg)
                self.tsys, self.tcomp = msg.get_srcSystem(), msg.get_srcComponent()
                self._enter("CAPABILITIES")
                self.caps_attempts = 0
                self._request_capabilities(now)
            elif (from_autopilot and self.state == "LINK_LOST"
                  and msg.get_srcSystem() == self.tsys):
                self._enter(self.resume)

        if self.state == "LINK_LOST":
            return

        if self.state == "CAPABILITIES":
            if kind == "AUTOPILOT_VERSION" and msg.get_srcSystem() == self.tsys:
                self.registry.on_autopilot_version(msg)
                self._begin_params(now)
        elif self.state == "PARAM_DOWNLOAD":
            self.params.on_message(msg, now)
        elif self.state == "CONFIGURE_STREAMS":
            self.telemetry.on_message(msg, now)
        elif self.state == "MISSION_DOWNLOAD":
            self.mission.on_message(msg, now)
        elif self.state == "OPERATIONAL":
            self._show_telemetry(msg, now)

    def tick(self, now: float) -> None:
        if self.state != "WAIT_HEARTBEAT":
            self._send_gcs_heartbeat(now)

        if self.registry.tick(now) and self.state not in ("LINK_LOST", "WAIT_HEARTBEAT"):
            self.resume = self.state  # повернемось саме туди, де нас обірвало
            self._enter("LINK_LOST")
            return
        if self.state in ("LINK_LOST", "WAIT_HEARTBEAT"):
            return

        self._update_pacing(now)

        if self.state == "CAPABILITIES":
            if now - self.caps_tx > CAPS_TIMEOUT:
                if self.caps_attempts >= CAPS_ATTEMPTS:
                    # Старий борт мовчить на #520: вважаємо, що можливостей немає.
                    print("[1/5] AUTOPILOT_VERSION не отримано — вважаємо стек застарілим")
                    self._begin_params(now)
                else:
                    self._request_capabilities(now)
        elif self.state == "PARAM_DOWNLOAD":
            self.params.tick(now)
            if self.params.done or self.params.failed:
                # Навіть неповний список краще за зупинку: далі йдемо з тим, що є.
                self._enter("CONFIGURE_STREAMS")
                self.telemetry.start(
                    self.tsys, self.tcomp,
                    self.registry.supports(mav.MAV_PROTOCOL_CAPABILITY_SET_MESSAGE_INTERVAL),
                    now,
                )
        elif self.state == "CONFIGURE_STREAMS":
            self.telemetry.tick(now)
            if self.telemetry.done:
                self._enter("MISSION_DOWNLOAD")
                self.mission.start(self.tsys, self.tcomp, now)
        elif self.state == "MISSION_DOWNLOAD":
            self.mission.tick(now)
            if self.mission.done or self.mission.failed:
                self._enter("OPERATIONAL")
                print(f"[5/5] рукостискання завершено: параметрів {len(self.params.values)}, "
                      f"точок місії {len(self.mission.items)}")

    def _request_capabilities(self, now: float) -> None:
        self.link.mav.command_long_send(
            self.tsys, self.tcomp,
            mav.MAV_CMD_REQUEST_AUTOPILOT_CAPABILITIES,
            self.caps_attempts,
            1.0,  # param1 = 1: надішли AUTOPILOT_VERSION
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
        )
        self.caps_tx = now
        self.caps_attempts += 1

    def _begin_params(self, now: float) -> None:
        self._enter("PARAM_DOWNLOAD")
        self.params.start(self.tsys, self.tcomp, now)

    def _send_gcs_heartbeat(self, now: float) -> None:
        # До першого почутого серцебиття станція в ефір не лізе взагалі; після —
        # сама шле 1 Гц, щоб борт бачив оператора й не спрацював failsafe.
        if now - self.last_gcs_hb < 1.0:
            return
        self.link.mav.heartbeat_send(mav.MAV_TYPE_GCS, mav.MAV_AUTOPILOT_INVALID, 0, 0,
                                     mav.MAV_STATE_ACTIVE)
        self.last_gcs_hb = now

    def _update_pacing(self, now: float) -> None:
        if now - self.last_pacing < PACING_PERIOD:
            return
        self.last_pacing = now

        stats = self.link.stats
        loss = stats.loss_percent
        gap = 0.4 if loss > 30.0 else 0.1
        self.params.pacing = gap
        self.mission.pacing = gap
        if loss > 30.0:
            print(f"[!] втрати {loss:.1f}% — сповільнюємо дозапити до {gap * 1000:.0f} мс")
        if stats.received == 0 and stats.parse_errors > 100:
            # Валідних кадрів немає, а сміття сиплеться — розбіжність швидкості UART.
            print(f"[!] {stats.parse_errors} помилок парсера без жодного кадру: "
                  f"перевірте швидкість порту")
        stats.reset_window()

    def _show_telemetry(self, msg, now: float) -> None:
        if msg.get_type() != "GLOBAL_POSITION_INT" or now - self.last_hud < 1.0:
            return
        self.last_hud = now
        print(f"[hud] {msg.lat * 1e-7:.7f}, {msg.lon * 1e-7:.7f}  "
              f"h={msg.relative_alt / 1000.0:.1f} м  курс={msg.hdg / 100.0:.1f}°  "
              f"втрати {self.link.stats.loss_percent:.1f}%")
