"""Черга наказів для сплячих вузлів і реєстр живих транзакцій."""

from __future__ import annotations

from collections import deque

from .models import CommandRecord


class Mailbox:
    """Поштова скринька: на кожен пристрій — своя черга cmd_id.

    Пристрій із постійним лінком дістає наказ по MQTT одразу, а той, що
    прокидається раз на кілька хвилин, забирає його з черги під час опитування.
    Прострочене відсіюється саме там — доставляти наказ, чий TTL сплив, гірше,
    ніж не доставити нічого.
    """

    def __init__(self) -> None:
        self._queues: dict[str, deque[str]] = {}
        self._records: dict[str, CommandRecord] = {}
        self._keys: dict[tuple[str, str], str] = {}

    def enqueue(self, record: CommandRecord) -> None:
        self._records[record.cmd_id] = record
        self._queues.setdefault(record.device_id, deque()).append(record.cmd_id)
        if record.idempotency_key:
            self._keys[(record.device_id, record.idempotency_key)] = record.cmd_id

    def get(self, cmd_id: str) -> CommandRecord | None:
        return self._records.get(cmd_id)

    def find_by_key(self, device_id: str, key: str) -> CommandRecord | None:
        cmd_id = self._keys.get((device_id, key))
        return self._records.get(cmd_id) if cmd_id else None

    def take_for(
        self, device_id: str, now: float
    ) -> tuple[CommandRecord | None, list[CommandRecord]]:
        """Віддати наказ пристроєві. Другим значенням — те, що протухло в черзі."""
        expired: list[CommandRecord] = []
        queue = self._queues.get(device_id)
        while queue:
            record = self._records.get(queue.popleft())
            if record is None or record.finished:
                continue
            if record.is_expired(now):
                record.mark_expired()
                expired.append(record)
                continue
            record.mark_dispatched(now)
            return record, expired
        return None, expired

    def expire_queued(self, now: float) -> list[CommandRecord]:
        """Протухле, до якого пристрій так і не прийшов."""
        dead = [
            record
            for record in self._records.values()
            if record.status == "QUEUED" and record.is_expired(now)
        ]
        for record in dead:
            record.mark_expired()
        return dead

    def overdue(self, now: float, deadline_sec: float) -> list[CommandRecord]:
        """Відправлене, по чому не прийшла друга фаза."""
        return [
            record
            for record in self._records.values()
            if not record.finished
            and record.dispatched_at is not None
            and now - record.dispatched_at > deadline_sec
        ]

    def active(self) -> list[CommandRecord]:
        return [record for record in self._records.values() if not record.finished]

    def purge(self, now: float, retention_sec: float) -> int:
        """Прибрати давно закриті транзакції, щоб реєстр не ріс без краю."""
        dead = [
            cmd_id
            for cmd_id, record in self._records.items()
            if record.finished and now - record.issued_at > retention_sec
        ]
        for cmd_id in dead:
            record = self._records.pop(cmd_id)
            if record.idempotency_key:
                self._keys.pop((record.device_id, record.idempotency_key), None)
        return len(dead)
