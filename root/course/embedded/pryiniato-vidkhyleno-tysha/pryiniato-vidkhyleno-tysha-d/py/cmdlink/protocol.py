"""Повідомлення MAVLink, потрібні для транзакції команди.

COMMAND_LONG (msgid 76), COMMAND_INT (msgid 75), COMMAND_ACK (msgid 77).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum


class MavResult(IntEnum):
    """Поле result у COMMAND_ACK."""

    ACCEPTED = 0
    TEMPORARILY_REJECTED = 1
    DENIED = 2
    UNSUPPORTED = 3
    FAILED = 4
    IN_PROGRESS = 5
    CANCELLED = 6
    COMMAND_LONG_ONLY = 7
    COMMAND_INT_ONLY = 8


RESULT_TEXT = {
    MavResult.ACCEPTED: "виконано",
    MavResult.TEMPORARILY_REJECTED: "тимчасово відхилено — стан апарата заважає",
    MavResult.DENIED: "заборонено контурами безпеки",
    MavResult.UNSUPPORTED: "прошивка не знає цієї команди",
    MavResult.FAILED: "збій виконання на борту",
    MavResult.IN_PROGRESS: "виконується",
    MavResult.CANCELLED: "перервано",
    MavResult.COMMAND_LONG_ONLY: "приймається лише в COMMAND_LONG",
    MavResult.COMMAND_INT_ONLY: "приймається лише в COMMAND_INT",
}


class TxState(IntEnum):
    """Стани клієнтського автомата транзакції."""

    IDLE = 0
    WAITING_ACK = 1
    IN_PROGRESS = 2
    SUCCESS = 3
    REJECTED = 4
    TIMEOUT_FAILURE = 5


class MavCmd(IntEnum):
    """Підмножина словника MAV_CMD, потрібна цьому прикладу."""

    NAV_LOITER_UNLIM = 17
    NAV_TAKEOFF = 22
    DO_SET_MODE = 176
    DO_DIGICAM_CONTROL = 203
    DO_GRIPPER = 211
    COMPONENT_ARM_DISARM = 400
    DO_START_MAG_CAL = 42424


class MavFrame(IntEnum):
    """Системи відліку для COMMAND_INT."""

    GLOBAL = 0
    GLOBAL_RELATIVE_ALT = 3
    GLOBAL_INT = 5
    GLOBAL_RELATIVE_ALT_INT = 6


class CopterMode(IntEnum):
    STABILIZE = 0
    AUTO = 3
    GUIDED = 4
    RTL = 6


# Накази з координатами: у COMMAND_LONG їх передавати не можна.
NAV_COMMANDS = frozenset({MavCmd.NAV_LOITER_UNLIM})
# Накази з фізичним спрацюванням: потрібен лічильник confirmation, тобто COMMAND_LONG.
LONG_ONLY_COMMANDS = frozenset(
    {MavCmd.DO_GRIPPER, MavCmd.DO_DIGICAM_CONTROL, MavCmd.COMPONENT_ARM_DISARM}
)

CUSTOM_MODE_ENABLED = 1.0   # прапорець base_mode у param1 команди DO_SET_MODE
FORCE_DISARM_MAGIC = 21196.0  # примусове глушіння моторів у повітрі

# Коди причини відмови в полі result_param2 нашої прошивки.
DENY_NO_GPS_FIX = 1
DENY_ARMED_IN_AIR = 2
DENY_EKF_NOT_READY = 3


@dataclass
class CommandLong:
    """Сім параметрів float32 плюс лічильник повторів."""

    command: int
    target_system: int = 1
    target_component: int = 1
    confirmation: int = 0
    params: list[float] = field(default_factory=lambda: [0.0] * 7)
    # Поля заголовка кадру, не тіла повідомлення: хто відправив.
    src_system: int = 255
    src_component: int = 190

    def __post_init__(self) -> None:
        if len(self.params) > 7:
            raise ValueError("COMMAND_LONG має рівно сім параметрів")
        self.params = [float(p) for p in self.params] + [0.0] * (7 - len(self.params))


@dataclass
class CommandInt:
    """Координати цілими ×1e7; поля confirmation тут НЕМАЄ."""

    command: int
    x: int = 0            # широта × 1e7
    y: int = 0            # довгота × 1e7
    z: float = 0.0        # висота в метрах за обраним frame
    frame: MavFrame = MavFrame.GLOBAL_RELATIVE_ALT_INT
    target_system: int = 1
    target_component: int = 1
    current: int = 0
    autocontinue: int = 0
    param1: float = 0.0
    param2: float = 0.0
    param3: float = 0.0
    param4: float = 0.0
    src_system: int = 255
    src_component: int = 190


@dataclass
class CommandAck:
    """Квитанція на конкретний номер команди."""

    command: int
    result: MavResult
    progress: int = 255      # 255 — прогрес не підтримується
    result_param2: int = 0
    target_system: int = 255  # кому адресовано (станція)
    target_component: int = 190
    src_system: int = 1       # із заголовка: хто відповів
    src_component: int = 1


def deg_to_1e7(deg: float) -> int:
    """Градуси → ціле ×1e7: сталий крок 1.1 см по всій земній кулі."""
    if not -180.0 <= deg <= 180.0:
        raise ValueError("координата поза межами [-180; 180] градусів")
    return int(round(deg * 1e7))


def deg_from_1e7(scaled: int) -> float:
    return scaled / 1e7
