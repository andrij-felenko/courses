"""Клієнтський автомат транзакції: надсилання, таймаут, повтор, квитанція."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, replace

from .protocol import RESULT_TEXT, CommandAck, CommandInt, CommandLong, MavResult, TxState

# Повний обіг кадру в реальному ефірі — 120…250 мс. Коротший таймаут не лікує
# втрату, а породжує шторм повторів і забиває буфер UART модема.
MIN_RETRY_INTERVAL = 0.25


@dataclass
class Outcome:
    state: TxState
    result: MavResult
    result_param2: int
    attempts: int          # скільки кадрів пішло в ефір
    message: str


class CommandClient:
    """Одна транзакція за раз: доки триває поточна, кнопка інтерфейсу заблокована.

    У бойовому коді на місці ``link`` стоїть з'єднання pymavlink, а ``transmit``
    зводиться до одного з двох викликів:

        conn.mav.command_long_send(f.target_system, f.target_component, f.command,
                                   f.confirmation, *f.params)
        conn.mav.command_int_send(f.target_system, f.target_component, f.frame,
                                  f.command, f.current, f.autocontinue,
                                  f.param1, f.param2, f.param3, f.param4,
                                  f.x, f.y, f.z)
    """

    def __init__(
        self,
        link,
        gcs_system: int = 255,
        gcs_component: int = 190,
        retry_interval: float = 0.8,
        max_retries: int = 3,
    ) -> None:
        if retry_interval < MIN_RETRY_INTERVAL:
            raise ValueError("інтервал повтору коротший за час обігу кадру — це шторм повторів")
        if not 1 <= max_retries <= 10:
            raise ValueError("MAX_RETRIES поза розумними межами 1…10")

        self.link = link
        self.gcs_system = gcs_system
        self.gcs_component = gcs_component
        self.retry_interval = retry_interval
        self.max_retries = max_retries

        self.state = TxState.IDLE
        self.last_outcome: Outcome | None = None
        self._frame: CommandLong | CommandInt | None = None
        self._acks: asyncio.Queue[CommandAck] | None = None

    @property
    def busy(self) -> bool:
        return self.state in (TxState.WAITING_ACK, TxState.IN_PROGRESS)

    async def send(self, frame: CommandLong | CommandInt, progress_cb=None) -> Outcome:
        """Проганяє транзакцію до термінального стану й повертає підсумок."""
        if self.busy:
            raise RuntimeError("транзакційний канал зайнятий попередньою командою")
        if frame.target_system == 0:
            # Широкомовний кадр отримають усі борти, а квитанцію не буде з ким зіставити.
            raise ValueError("широкомовна адреса 0 заборонена для командної транзакції")

        # Працюємо з власною копією: лічильник повторів міняємо ми, не викликач.
        self._frame = replace(frame)
        if isinstance(self._frame, CommandLong):
            self._frame.confirmation = 0  # нова окрема дія завжди починається з нуля
        self._frame.src_system = self.gcs_system
        self._frame.src_component = self.gcs_component

        self._acks = asyncio.Queue()
        self.state = TxState.WAITING_ACK
        try:
            outcome = await self._run(progress_cb)
        finally:
            self._acks = None
            self._frame = None
        self.last_outcome = outcome
        return outcome

    async def _run(self, progress_cb) -> Outcome:
        assert self._acks is not None and self._frame is not None
        attempt = 0
        while True:
            self.link.transmit(self._frame)
            timed_out = False
            while True:
                try:
                    ack = await asyncio.wait_for(self._acks.get(), self.retry_interval)
                except asyncio.TimeoutError:
                    timed_out = True
                    break

                if ack.result == MavResult.IN_PROGRESS:
                    # Довга операція жива: таймер очікування починається наново.
                    self.state = TxState.IN_PROGRESS
                    if progress_cb is not None and ack.progress != 255:
                        progress_cb(ack.progress)
                    continue

                if ack.result == MavResult.ACCEPTED:
                    self.state = TxState.SUCCESS
                    return Outcome(TxState.SUCCESS, ack.result, ack.result_param2,
                                   attempt + 1, "команду виконано")

                # Пакет дійшов, борт відмовив — вердикт остаточний, повтори заборонені.
                self.state = TxState.REJECTED
                return Outcome(TxState.REJECTED, ack.result, ack.result_param2, attempt + 1,
                               f"борт відмовив: {RESULT_TEXT[ack.result]}")

            if not timed_out:  # захист від мовчазної зміни логіки вище
                continue
            if attempt >= self.max_retries:
                self.state = TxState.TIMEOUT_FAILURE
                return Outcome(TxState.TIMEOUT_FAILURE, MavResult.FAILED, 0, attempt + 1,
                               "тиша: борт не відповів, фізичний стан апарата НЕВІДОМИЙ")

            attempt += 1
            if isinstance(self._frame, CommandLong):
                # Лічильник повторів: борт бачить, що транзакція та сама, і не
                # виконує неідемпотентну дію вдруге.
                self._frame.confirmation = attempt
            # COMMAND_INT поля confirmation не має — повтор іде байт-у-байт,
            # тому цим контейнером шлють лише ідемпотентні навігаційні накази.
            self.state = TxState.WAITING_ACK

    def on_ack(self, ack: CommandAck) -> None:
        """Виклик із приймального тракту на КОЖЕН COMMAND_ACK у потоці."""
        if not self.busy or self._acks is None or self._frame is None:
            return
        if ack.command != self._frame.command:
            return  # квитанція на іншу команду з фонового потоку
        if (ack.src_system != self._frame.target_system
                or ack.src_component != self._frame.target_component):
            return  # відповів не той компонент, якому ми адресували наказ
        if ack.target_system != 0 and (ack.target_system != self.gcs_system
                                       or ack.target_component != self.gcs_component):
            return  # квитанція адресована іншій станції в тій самій мережі
        self._acks.put_nowait(ack)
