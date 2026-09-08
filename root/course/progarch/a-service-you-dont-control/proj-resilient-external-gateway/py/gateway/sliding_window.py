"""
Ковзне вікно на базі кільцевого буфера для обліку надійності та латентності.
"""

from collections import deque
from typing import Deque

from gateway.models import CallResult, SlidingWindowConfig


class SlidingWindow:
    """
    Кільцевий буфер фіксованого розміру для відстеження статистики викликів.
    
    Запобігає хибним спрацюванням запобіжника на малих вибірках (small sample variance),
    вимагаючи накопичення щонайменше min_call_threshold (N_min) спостережень.
    """

    def __init__(self, config: SlidingWindowConfig = SlidingWindowConfig()) -> None:
        self._config = config
        self._buffer: Deque[CallResult] = deque(maxlen=config.window_size)

    @property
    def total_calls(self) -> int:
        """Поточна кількість накопичених викликів у вікні."""
        return len(self._buffer)

    @property
    def failed_calls(self) -> int:
        """Кількість невдалих або перерваних викликів."""
        return sum(1 for call in self._buffer if not call.is_success)

    @property
    def slow_calls(self) -> int:
        """Кількість викликів із неприпустимо великою латентністю."""
        return sum(1 for call in self._buffer if call.is_slow and call.is_success)

    @property
    def failure_rate(self) -> float:
        """Частка збоїв серед накопичених викликів (від 0.0 до 1.0)."""
        if not self._buffer:
            return 0.0
        return self.failed_calls / len(self._buffer)

    @property
    def slow_call_rate(self) -> float:
        """Частка повільних запитів серед накопичених викликів."""
        if not self._buffer:
            return 0.0
        return self.slow_calls / len(self._buffer)

    def record(self, result: CallResult) -> None:
        """Додає новий результат виклику в кільцевий буфер."""
        self._buffer.append(result)

    def should_trip(self) -> bool:
        """
        Перевіряє, чи перевищено критичні пороги надійності для розмикання ланцюга.
        
        Якщо кількість спостережень менша за N_min, розрахунок блокується, щоб
        уникнути хибного розмикання через випадковий одиночний збій.
        """
        if self.total_calls < self._config.min_call_threshold:
            return False

        return (
            self.failure_rate >= self._config.failure_rate_threshold
            or self.slow_call_rate >= self._config.slow_call_rate_threshold
        )

    def reset(self) -> None:
        """Очищує буфер вікна після відновлення працездатності сервісу."""
        self._buffer.clear()
