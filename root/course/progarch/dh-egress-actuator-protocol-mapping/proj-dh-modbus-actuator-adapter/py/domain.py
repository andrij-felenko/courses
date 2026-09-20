"""
Доменний шар керування опалювальним актуатором (платформа Digital Homes).

Містить контракт вихідного порту (Driven Port), незмінний об'єкт-значення (Value Object)
позиції клапана, функційний контейнер результату (Result) та типізовану ієрархію
доменних помилок. Повністю ізольований від апаратних протоколів (Modbus, CAN),
фізичних шин (RS-485) та низькорівневих системних винятків.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
import math
from typing import Generic, Optional, TypeVar

T = TypeVar("T")
E = TypeVar("E")


# ============================================================================
# РЕЗУЛЬТАТ (RESULT PATTERN)
# ============================================================================

@dataclass(frozen=True)
class Result(Generic[T, E]):
    """
    Універсальний типізований контейнер результату операції (Ok або Err).

    Забезпечує безпечну передачу результату без протікання винятків крізь
    архітектурні межі. Примушує клієнтський код явно обробляти сценарії успіху й помилок.
    """

    _value: Optional[T] = None
    _error: Optional[E] = None
    _is_ok: bool = True

    @classmethod
    def ok(cls, value: T) -> Result[T, E]:
        """Створити успішний результат із корисним значенням."""
        return cls(_value=value, _error=None, _is_ok=True)

    @classmethod
    def err(cls, error: E) -> Result[T, E]:
        """Створити результат із типізованою помилкою."""
        return cls(_value=None, _error=error, _is_ok=False)

    @property
    def is_ok(self) -> bool:
        """Повертає True, якщо операція завершилася успішно."""
        return self._is_ok

    @property
    def is_err(self) -> bool:
        """Повертає True, якщо операція завершилася з помилкою."""
        return not self._is_ok

    def unwrap(self) -> T:
        """
        Повертає значення у разі успіху або збуджує RuntimeError, якщо результат є помилкою.
        """
        if not self._is_ok:
            raise RuntimeError(f"Спроба розпакувати помилковий Result: {self._error}")
        return self._value  # type: ignore[return-value]

    def unwrap_err(self) -> E:
        """
        Повертає помилку або збуджує RuntimeError, якщо результат є успішним.
        """
        if self._is_ok:
            raise RuntimeError(f"Спроба розпакувати успішний Result як помилку: {self._value}")
        return self._error  # type: ignore[return-value]

    def value_or(self, default: T) -> T:
        """Повертає значення у разі успіху або вказане значення за замовчуванням."""
        return self._value if self._is_ok else default


# ============================================================================
# ДОМЕННІ ПОМИЛКИ АКТУАТОРА (ТИПІЗОВАНА ІЄРАРХІЯ)
# ============================================================================

class ActuatorError(Exception):
    """
    Базовий клас закритої ієрархії типізованих доменних помилок актуатора.

    Доменне ядро оперує виключно цими типами й не залежить від кодів винятків
    Modbus, таймаутів сокетів чи збоїв CRC на послідовній лінії.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(message={self.message!r})"


class ActuatorUnresponsive(ActuatorError):
    """
    Актуатор не відповів за відведений ліміт часу.

    Спричиняється обривом фізичної лінії RS-485, вимкненням живлення клапана
    або невідповідністю адреси веденого вузла (Slave ID).
    """
    pass


class ActuatorHardwareFault(ActuatorError):
    """
    Внутрішній апаратний збій актуатора.

    Відповідає аварійному стану сервоприводу: перегрів двигуна, заклинювання штока,
    помилка позиційного енкодера або протокольний код Modbus 0x04 (Slave Device Failure).
    """
    pass


class ActuatorProtocolError(ActuatorError):
    """
    Помилка протокольного рівня або цілісності даних.

    Спричиняється багаторазовим спотворенням CRC-16 через електромагнітні завади,
    неприпустимою адресою регістра (код 0x02) або непідтримуваною функцією (код 0x01).
    """
    pass


# ============================================================================
# ОБ'ЄКТ-ЗНАЧЕННЯ (VALUE OBJECT)
# ============================================================================

@dataclass(frozen=True)
class ValvePosition:
    """
    Незмінний об'єкт-значення (Value Object) відсотка відкриття клапана.

    Інкапсулює інваріант валідності фізичного діапазону [0.0%, 100.0%].
    Унеможливлює потрапляння в систему від'ємних чисел, переповнення або NaN.
    """

    percent: float

    def __post_init__(self) -> None:
        if math.isnan(self.percent) or math.isinf(self.percent):
            raise ValueError(f"Позиція клапана не може бути NaN або Inf: {self.percent}")
        if not (0.0 <= self.percent <= 100.0):
            raise ValueError(
                f"Позиція клапана виходить за допустимі межі [0.0..100.0]%: {self.percent}"
            )

    @classmethod
    def closed(cls) -> ValvePosition:
        """Фабричний метод: повністю закритий клапан (0.0%)."""
        return cls(0.0)

    @classmethod
    def fully_open(cls) -> ValvePosition:
        """Фабричний метод: повністю відкритий клапан (100.0%)."""
        return cls(100.0)


# ============================================================================
# ВИХІДНИЙ ПОРТ (DRIVEN PORT)
# ============================================================================

class HeatingValveActuatorPort(ABC):
    """
    Абстрактний інтерфейс вихідного керованого порту (Driven Port).

    Визначає контракт надсилання команд позиціонування виконавчому механізму
    опалення. Домен викликає цей контракт, не підозрюючи про протокол передачі.
    """

    @abstractmethod
    async def set_position(self, position: ValvePosition) -> Result[None, ActuatorError]:
        """
        Асинхронно передати уставку відкриття виконавчому приводу клапана.

        :param position: Валідований доменний об'єкт-значення позиції.
        :return: Result.ok(None) при успішному підтвердженні актуатором або
                 Result.err(ActuatorError) у разі апаратної чи комунікаційної відмови.
        """
        raise NotImplementedError
