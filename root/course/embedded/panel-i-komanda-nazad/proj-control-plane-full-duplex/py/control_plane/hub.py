"""Широкомовна трансляція станів у відкриті панелі операторів."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from fastapi import WebSocket

LOG = logging.getLogger("control-plane.hub")


class Hub:
    """Набір живих WebSocket-підключень.

    Панелей у зміні кілька, і всі мають бачити одне й те саме: команду
    надіслав один оператор, а стан заслінки стосується всіх.
    """

    def __init__(self) -> None:
        self._sockets: set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def register(self, socket: WebSocket) -> None:
        async with self._lock:
            self._sockets.add(socket)

    async def unregister(self, socket: WebSocket) -> None:
        async with self._lock:
            self._sockets.discard(socket)

    async def send(self, socket: WebSocket, payload: dict[str, Any]) -> None:
        try:
            await socket.send_json(payload)
        except (RuntimeError, ConnectionError):
            # Сокет уже мертвий: прибираємо, і хай клієнт перепідключається.
            await self.unregister(socket)

    async def broadcast(self, payload: dict[str, Any]) -> None:
        async with self._lock:
            targets = list(self._sockets)
        dead: list[WebSocket] = []
        for socket in targets:
            try:
                await socket.send_json(payload)
            except (RuntimeError, ConnectionError) as exc:
                LOG.info("панель відпала під час трансляції: %s", exc)
                dead.append(socket)
        if dead:
            async with self._lock:
                self._sockets.difference_update(dead)
