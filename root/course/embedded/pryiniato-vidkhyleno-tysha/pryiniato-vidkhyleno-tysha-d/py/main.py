import time
import asyncio
from enum import IntEnum
from typing import Callable, Optional, Dict, Any

class MavResult(IntEnum):
    ACCEPTED = 0
    TEMPORARILY_REJECTED = 1
    DENIED = 2
    UNSUPPORTED = 3
    FAILED = 4
    IN_PROGRESS = 5
    CANCELLED = 6
    COMMAND_LONG_ONLY = 7
    COMMAND_INT_ONLY = 8

class TransactionState(IntEnum):
    IDLE = 0
    WAITING_ACK = 1
    IN_PROGRESS = 2
    SUCCESS = 3
    REJECTED = 4
    TIMEOUT_FAILURE = 5

class MavlinkCommandClient:
    """
    Асинхронний менеджер транзакцій команд MAVLink для наземних станцій та companion комп'ютерів.
    """
    def __init__(self, mav_connection, retry_interval_sec: float = 1.0, max_retries: int = 3):
        self.mav = mav_connection
        self.retry_interval = retry_interval_sec
        self.max_retries = max_retries
        self.state = TransactionState.IDLE
        self._current_task: Optional[asyncio.Future] = None
        self._progress_cb: Optional[Callable[[int], None]] = None

    async def execute_command(self, target_sys: int, target_comp: int, command_id: int,
                              params: list[float], 
                              progress_callback: Optional[Callable[[int], None]] = None) -> Dict[str, Any]:
        """
        Відправляє команду та очікує завершення транзакції через механізм повторів і таймаутів.
        """
        if self.state in (TransactionState.WAITING_ACK, TransactionState.IN_PROGRESS):
            raise RuntimeError("Транзакційний канал зайнятий попередньою командою")

        self.state = TransactionState.WAITING_ACK
        self._progress_cb = progress_callback
        loop = asyncio.get_running_loop()
        self._current_task = loop.create_future()

        confirmation = 0
        try:
            for attempt in range(self.max_retries + 1):
                # Відправка кадру COMMAND_LONG
                self._send_command_long(target_sys, target_comp, command_id, confirmation, params)
                
                # Очікування відповіді ACK із заданим таймаутом
                try:
                    outcome = await asyncio.wait_for(
                        asyncio.shield(self._current_task), 
                        timeout=self.retry_interval
                    )
                    return outcome
                except asyncio.TimeoutError:
                    if attempt < self.max_retries:
                        confirmation += 1
                        self.state = TransactionState.WAITING_ACK
                        continue # Наступна спроба
                    else:
                        self.state = TransactionState.TIMEOUT_FAILURE
                        return {
                            "success": False,
                            "state": TransactionState.TIMEOUT_FAILURE,
                            "result": MavResult.FAILED,
                            "message": "Таймаут: борт не відповів після всіх спроб"
                        }
        finally:
            self.state = TransactionState.IDLE
            self._current_task = None
            self._progress_cb = None

    def on_command_ack_received(self, msg) -> None:
        """
        Колбек обробки повідомлення COMMAND_ACK із загального потоку телеметрії.
        """
        if self.state not in (TransactionState.WAITING_ACK, TransactionState.IN_PROGRESS):
            return

        command = msg.command
        result = MavResult(msg.result)
        progress = getattr(msg, 'progress', 255)
        result_param2 = getattr(msg, 'result_param2', 0)

        if self._current_task is None or self._current_task.done():
            return

        if result == MavResult.IN_PROGRESS:
            self.state = TransactionState.IN_PROGRESS
            if self._progress_cb and progress != 255:
                self._progress_cb(progress)
            return

        if result == MavResult.ACCEPTED:
            self.state = TransactionState.SUCCESS
            self._current_task.set_result({
                "success": True,
                "state": TransactionState.SUCCESS,
                "result": result,
                "result_param2": result_param2,
                "message": "Команду успішно виконано"
            })
        else:
            self.state = TransactionState.REJECTED
            self._current_task.set_result({
                "success": False,
                "state": TransactionState.REJECTED,
                "result": result,
                "result_param2": result_param2,
                "message": f"Команду відхилено бортом (код {result.name})"
            })

    def _send_command_long(self, target_sys: int, target_comp: int, command_id: int,
                           confirmation: int, params: list[float]) -> None:
        p = (params + [0.0] * 7)[:7]
        # Виклик бібліотеки pymavlink:
        # self.mav.mav.command_long_send(target_sys, target_comp, command_id, confirmation, *p)
        print(f"[TX pymavlink] cmd={command_id} target=({target_sys}:{target_comp}) conf={confirmation}")
