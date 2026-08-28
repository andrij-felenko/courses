# dh_jobs.py — робочий маршрутизатор фонових задач DH.  Запуск: python dh_jobs.py
from contextlib import contextmanager
from dataclasses import dataclass
from types import SimpleNamespace


class Db:
    """Мінімальна, але ЧЕСНА модель БД: вставлене в транзакції видно лише після commit()."""
    def __init__(self):
        self.tables: dict[str, list[dict]] = {}

    def table(self, name: str) -> list[dict]:
        return self.tables.setdefault(name, [])     # закомічені рядки цієї таблиці

    def begin(self) -> "Tx":
        return Tx(self)


class Tx:
    def __init__(self, db: Db):
        self.db = db
        self.staged: list[tuple[str, dict]] = []    # буфер: ще НЕ закомічені вставки
        self.done = False

    def insert(self, table: str, row: dict) -> None:
        if self.done:
            raise RuntimeError("транзакція вже завершена")
        self.staged.append((table, row))            # просто складаємо в буфер — у таблицю ще нічого

    def commit(self) -> None:
        if self.done:
            raise RuntimeError("подвійний commit")
        for table, row in self.staged:              # одним махом: усе або нічого
            self.db.table(table).append(row)
        self.done = True

    def rollback(self) -> None:
        self.staged = []                            # викидаємо буфер — жоден рядок не осів
        self.done = True


@contextmanager
def transaction(db: Db):
    """Ідіоматична обгортка: коміт на успіх, відкат на будь-який виняток."""
    tx = db.begin()
    try:
        yield tx
        tx.commit()
    except Exception:
        tx.rollback()                               # впало до commit → нічого не осіло
        raise
