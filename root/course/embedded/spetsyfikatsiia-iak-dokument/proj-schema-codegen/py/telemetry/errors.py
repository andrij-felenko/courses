"""Коди помилок розбору — дзеркало proto_status_t з c/telemetry_protocol.h.

Бекенд і прошивка відкидають кадр за однаковими підставами й називають їх
однаково: інакше «сервер прийняв, а вузол ні» доводиться розплутувати за
логами двох команд.
"""

from __future__ import annotations

from enum import Enum


class ParseError(Enum):
    INVALID_SOF = "ERR_INVALID_SOF"
    INVALID_EOF = "ERR_INVALID_EOF"
    INVALID_LEN = "ERR_INVALID_LEN"
    INVALID_CRC = "ERR_INVALID_CRC"
    UNKNOWN_MSG = "ERR_UNKNOWN_MSG"
    UNSUPPORTED_VERSION = "ERR_UNSUPPORTED_VERSION"

    def __str__(self) -> str:  # у логах хочеться саме код, а не ParseError.…
        return self.value


class ProtocolError(Exception):
    """Кадр відкинуто. Код — машинам, detail — людині в лог."""

    def __init__(self, code: ParseError, detail: str = "") -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code.value}: {detail}" if detail else code.value)
