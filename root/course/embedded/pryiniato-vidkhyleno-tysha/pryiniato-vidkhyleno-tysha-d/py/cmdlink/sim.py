"""Другий бік каналу: борт із кешем дедуплікації та радіо з втратами.

Часу тут не вигадуємо — його дає планувальник asyncio, тож затримки й таймаути
живуть у тій самій шкалі, що й у справжньому з'єднанні.
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, replace

from .protocol import (
    CUSTOM_MODE_ENABLED,
    DENY_ARMED_IN_AIR,
    DENY_EKF_NOT_READY,
    DENY_NO_GPS_FIX,
    FORCE_DISARM_MAGIC,
    LONG_ONLY_COMMANDS,
    NAV_COMMANDS,
    CommandAck,
    CommandInt,
    CommandLong,
    CopterMode,
    MavCmd,
    MavFrame,
    MavResult,
    deg_from_1e7,
)


@dataclass
class _CacheEntry:
    target_system: int
    target_component: int
    command: int
    last_confirmation: int
    result: MavResult
    result_param2: int
    stamp: float


class SimAutopilot:
    """Перевірки безпеки, кеш транзакцій і довга операція з прогресом."""

    TX_WINDOW = 3.0  # вікно транзакції: пізніший повтор вважається новим наказом

    def __init__(self, system_id: int = 1, component_id: int = 1) -> None:
        self.system_id = system_id
        self.component_id = component_id

        # Важелі сценарію заняття.
        self.powered = True
        self.gps_fix = False
        self.ekf_ready = True
        self.dedup = True

        self.armed = False
        self.in_air = False
        self.mode = CopterMode.STABILIZE
        self.gripper_closed = False
        self.gripper_actuations = 0
        self.photos = 0
        self.loiter: tuple[float, float, float] | None = None

        self._cache: _CacheEntry | None = None
        self._reports: list[tuple[float, CommandAck]] = []

    def take_reports(self) -> list[tuple[float, CommandAck]]:
        """Відкладені звіти довгої операції: (затримка від зараз, квитанція)."""
        reports, self._reports = self._reports, []
        return reports

    def handle(self, frame: CommandLong | CommandInt) -> CommandAck | None:
        """None означає тишу: борт знеструмлено, завис або кадр не йому."""
        if not self.powered:
            return None
        if frame.target_system != self.system_id:
            return None
        if frame.target_component not in (0, self.component_id):
            return None
        if isinstance(frame, CommandInt):
            # Дедуплікації немає: у COMMAND_INT немає поля confirmation, тому
            # повтор не відрізнити від нового наказу.
            return self._execute_int(frame)
        return self._handle_long(frame)

    def _handle_long(self, frame: CommandLong) -> CommandAck:
        now = time.monotonic()
        cache = self._cache
        same_transaction = (
            cache is not None
            and cache.command == frame.command
            and cache.target_system == frame.target_system
            and cache.target_component == frame.target_component
            and now - cache.stamp <= self.TX_WINDOW
        )

        if self.dedup and frame.confirmation > 0 and same_transaction:
            # Станція не почула ACK і повторює ту саму транзакцію. Виконавчий
            # механізм НЕ чіпаємо — віддаємо збережений результат ще раз.
            print(f"  [борт] повтор conf={frame.confirmation} упізнано кешем, дію не повторюємо")
            cache.last_confirmation = frame.confirmation
            return self._ack(frame, cache.result, cache.result_param2)

        ack = self._execute_long(frame, now)
        self._cache = _CacheEntry(
            target_system=frame.target_system,
            target_component=frame.target_component,
            command=frame.command,
            last_confirmation=frame.confirmation,
            result=ack.result,
            result_param2=ack.result_param2,
            stamp=now,
        )
        return ack

    def _execute_long(self, frame: CommandLong, now: float) -> CommandAck:
        p = frame.params
        command = frame.command

        if command == MavCmd.COMPONENT_ARM_DISARM:
            if p[0] > 0.5:
                if not self.gps_fix:
                    return self._ack(frame, MavResult.DENIED, DENY_NO_GPS_FIX)
                self.armed = True  # ідемпотентно: повторний ARM нічого не змінює
                return self._ack(frame, MavResult.ACCEPTED)
            if self.in_air and p[1] != FORCE_DISARM_MAGIC:
                return self._ack(frame, MavResult.DENIED, DENY_ARMED_IN_AIR)
            self.armed = False
            self.in_air = False
            return self._ack(frame, MavResult.ACCEPTED)

        if command == MavCmd.DO_SET_MODE:
            if p[0] != CUSTOM_MODE_ENABLED:
                return self._ack(frame, MavResult.UNSUPPORTED)
            wanted = int(p[1])
            if wanted not in tuple(CopterMode):
                return self._ack(frame, MavResult.UNSUPPORTED)  # прошивка такого режиму не має
            if wanted == CopterMode.AUTO and not self.ekf_ready:
                # Динамічний стан заважає просто зараз — за кілька секунд варто повторити.
                return self._ack(frame, MavResult.TEMPORARILY_REJECTED, DENY_EKF_NOT_READY)
            self.mode = CopterMode(wanted)  # абсолютний цільовий стан: ідемпотентно
            return self._ack(frame, MavResult.ACCEPTED)

        if command == MavCmd.NAV_TAKEOFF:
            if not self.armed:
                return self._ack(frame, MavResult.TEMPORARILY_REJECTED)
            self.in_air = True
            return self._ack(frame, MavResult.ACCEPTED)

        if command == MavCmd.DO_GRIPPER:
            action = int(p[1])  # 0 — відпустити, 1 — захопити, 2 — перемкнути
            if action == 2:
                self.gripper_closed = not self.gripper_closed
            elif action in (0, 1):
                self.gripper_closed = action == 1
            else:
                return self._ack(frame, MavResult.FAILED)
            self.gripper_actuations += 1  # сервопривід реально клацнув
            state_text = "закрито" if self.gripper_closed else "відкрито"
            print(f"  [борт] замок спрацював, тепер {state_text} "
                  f"(усього спрацювань: {self.gripper_actuations})")
            return self._ack(frame, MavResult.ACCEPTED)

        if command == MavCmd.DO_DIGICAM_CONTROL:
            if p[4] > 0.5:
                self.photos += 1  # затвор клацнув — теж неідемпотентна дія
            return self._ack(frame, MavResult.ACCEPTED)

        if command == MavCmd.DO_START_MAG_CAL:
            # Довга операція: одразу IN_PROGRESS, далі періодичні звіти прогресу
            # й фінальний ACCEPTED. Кожен звіт скидає таймаут станції.
            self._reports = [
                (0.2, self._ack(frame, MavResult.IN_PROGRESS, progress=25)),
                (0.4, self._ack(frame, MavResult.IN_PROGRESS, progress=50)),
                (0.6, self._ack(frame, MavResult.IN_PROGRESS, progress=75)),
                (0.8, self._ack(frame, MavResult.ACCEPTED)),
            ]
            return self._ack(frame, MavResult.IN_PROGRESS, progress=0)

        if command in NAV_COMMANDS:
            # Навігаційний наказ у неправильному контейнері: координати у float32
            # втратили б понад 40 см ще до розбору.
            return self._ack(frame, MavResult.COMMAND_INT_ONLY)
        return self._ack(frame, MavResult.UNSUPPORTED)

    def _execute_int(self, frame: CommandInt) -> CommandAck:
        if frame.command == MavCmd.NAV_LOITER_UNLIM:
            if frame.frame not in (MavFrame.GLOBAL_INT, MavFrame.GLOBAL_RELATIVE_ALT_INT):
                return self._ack(frame, MavResult.UNSUPPORTED)
            self.loiter = (deg_from_1e7(frame.x), deg_from_1e7(frame.y), frame.z)
            print(f"  [борт] точка очікування: {self.loiter[0]:.7f}, "
                  f"{self.loiter[1]:.7f} на {self.loiter[2]} м")
            return self._ack(frame, MavResult.ACCEPTED)
        if frame.command in LONG_ONLY_COMMANDS:
            # Ці накази несуть лічильник повторів, тож приймаються лише в COMMAND_LONG.
            return self._ack(frame, MavResult.COMMAND_LONG_ONLY)
        return self._ack(frame, MavResult.UNSUPPORTED)

    def _ack(self, frame, result: MavResult, result_param2: int = 0,
             progress: int = 255) -> CommandAck:
        return CommandAck(
            command=frame.command,
            result=result,
            progress=progress,
            result_param2=result_param2,
            target_system=frame.src_system,
            target_component=frame.src_component,
            src_system=self.system_id,
            src_component=self.component_id,
        )


class SimRadio:
    """Напівдуплексний канал: слот угору, обробка на борту, слот униз."""

    QUEUE_DEPTH = 4  # глибина черги кадрів у модемі; далі буфер UART переповнюється

    def __init__(self, vehicle: SimAutopilot, up_delay: float = 0.06,
                 down_delay: float = 0.06) -> None:
        self.vehicle = vehicle
        self.up_delay = up_delay
        self.down_delay = down_delay
        self.client = None
        self._drop_up = 0
        self._drop_down = 0
        self._in_flight = 0
        self._tasks: set[asyncio.Task] = set()

    def attach(self, client) -> None:
        self.client = client

    def drop_next_uplink(self, frames: int) -> None:
        self._drop_up = frames

    def drop_next_downlink(self, frames: int) -> None:
        self._drop_down = frames

    def transmit(self, frame: CommandLong | CommandInt) -> None:
        """Синхронний запис кадру в модем — так само поводиться pymavlink."""
        if isinstance(frame, CommandLong):
            print(f"  [TX] COMMAND_LONG cmd={int(frame.command)} "
                  f"ціль={frame.target_system}:{frame.target_component} "
                  f"conf={frame.confirmation}")
        else:
            print(f"  [TX] COMMAND_INT cmd={int(frame.command)} "
                  f"ціль={frame.target_system}:{frame.target_component} "
                  f"x={frame.x} y={frame.y}")

        if self._drop_up > 0:
            self._drop_up -= 1
            print("  [ефір] кадр Uplink спотворено шумом, CRC не зійшлася")
            return
        if self._in_flight >= self.QUEUE_DEPTH:
            print("  [ефір] буфер UART модема переповнено — кадр відкинуто")
            return

        self._in_flight += 1
        # Кадр летить власною копією: наступний повтор змінить лічильник в оригіналі.
        self._spawn(self._uplink(replace(frame)))

    async def _uplink(self, frame) -> None:
        try:
            await asyncio.sleep(self.up_delay)
            ack = self.vehicle.handle(frame)
            reports = self.vehicle.take_reports()
        finally:
            self._in_flight -= 1

        if ack is not None:
            self._spawn(self._downlink(ack, self.down_delay))
        for delay, report in reports:
            self._spawn(self._downlink(report, self.down_delay + delay))

    async def _downlink(self, ack: CommandAck, delay: float) -> None:
        await asyncio.sleep(delay)
        if self._drop_down > 0:
            self._drop_down -= 1
            print("  [ефір] квитанція Downlink загинула — дія на борту ВЖЕ виконана")
            return
        if self.client is not None:
            self.client.on_ack(ack)

    def _spawn(self, coro) -> None:
        task = asyncio.ensure_future(coro)
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)

    async def drain(self) -> None:
        """Дочекатися кадрів, що ще в ефірі, — інакше вони помруть із циклом."""
        while self._tasks:
            await asyncio.gather(*list(self._tasks))
