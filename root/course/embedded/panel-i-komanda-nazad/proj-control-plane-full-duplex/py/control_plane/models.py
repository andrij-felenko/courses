"""Тіла запитів, звітів заліза і сам запис транзакції."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel, Field

# Статуси, після яких транзакція вже нікуди не рухається.
TERMINAL: frozenset[str] = frozenset(
    {"COMPLETED", "FAILED", "EXPIRED", "TIMEOUT", "REJECTED"}
)


class CommandRequest(BaseModel):
    """Те, що надсилає панель оператора в POST /command."""

    device_id: str = Field(min_length=1, max_length=64)
    op: str = Field(min_length=1, max_length=64)
    params: dict[str, Any] = Field(default_factory=dict)
    ttl_sec: int = Field(default=300, ge=1, le=86_400)
    # Ключ ідемпотентності генерує браузер: повторний клік чи ретрай мережі
    # не має породжувати другу транзакцію.
    idempotency_key: str | None = Field(default=None, max_length=64)


@dataclass(slots=True)
class DeviceReport:
    """Квитанція або звіт про рух, що прийшли з теми devices/<id>/cmd/#."""

    cmd_id: str
    state: str
    progress_pct: int = 0
    value_pct: int = 0
    error_code: int = 0

    @classmethod
    def from_payload(cls, raw: bytes | str) -> DeviceReport:
        """Розібрати кадр заліза. Кидає ValueError на будь-якому непотребі."""
        data = json.loads(raw)  # json.JSONDecodeError успадкований від ValueError
        if not isinstance(data, dict):
            raise ValueError("кадр не є об'єктом JSON")

        cmd_id = data.get("cmd_id")
        # Квитанція фази 1 приходить полем status, звіт про рух — полем state.
        state = data.get("state") or data.get("status")
        if not cmd_id or not state:
            raise ValueError("у кадрі немає cmd_id або стану")

        return cls(
            cmd_id=str(cmd_id),
            state=str(state),
            progress_pct=int(data.get("progress_pct", 0)),
            value_pct=int(data.get("value_pct", 0)),
            error_code=int(data.get("err", data.get("error_code", 0))),
        )


@dataclass(slots=True)
class CommandRecord:
    """Стан однієї транзакції в пам'яті диспетчера."""

    cmd_id: str
    device_id: str
    op: str
    params: dict[str, Any]
    ttl_sec: int
    operator: str
    idempotency_key: str | None = None
    issued_at: float = field(default_factory=time.time)
    dispatched_at: float | None = None
    status: str = "QUEUED"
    progress_pct: int = 0
    value_pct: int = 0
    error_code: int = 0

    @property
    def expires_at(self) -> float:
        return self.issued_at + self.ttl_sec

    @property
    def finished(self) -> bool:
        return self.status in TERMINAL

    def is_expired(self, now: float) -> bool:
        return now > self.expires_at

    def mark_dispatched(self, now: float | None = None) -> None:
        self.dispatched_at = time.time() if now is None else now
        self.status = "DISPATCHED"

    def mark_expired(self) -> None:
        self.status = "EXPIRED"
        self.error_code = 104

    def mark_timeout(self) -> None:
        self.status = "TIMEOUT"
        self.error_code = 408

    def apply(self, report: DeviceReport) -> bool:
        """Накласти звіт заліза. False — стан не змінився, транслювати нічого."""
        if self.finished:
            # Запізнілий звіт по вже закритій транзакції її не воскрешає:
            # інакше після TIMEOUT панель показувала б рух заднім числом.
            return False
        self.status = report.state
        self.progress_pct = report.progress_pct
        self.value_pct = report.value_pct
        self.error_code = report.error_code
        return True

    def snapshot(self) -> dict[str, Any]:
        return {
            "cmd_id": self.cmd_id,
            "device_id": self.device_id,
            "op": self.op,
            "status": self.status,
            "progress_pct": self.progress_pct,
            "value_pct": self.value_pct,
            "error_code": self.error_code,
            "issued_at": round(self.issued_at, 3),
        }
