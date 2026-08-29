"""Кадрувальник байтового потоку: ковзне вікно з ресинхронізацією.

UART, RS-485 і TCP віддають потік БЕЗ меж повідомлень. Приймач може
увімкнутися посеред кадру, а перешкода — з'їсти байт. Тому межу шукають так:
дійти до синхробайта, добрати решту кадру, судити за CRC; не зійшлося —
крок на один байт уперед і спочатку.
"""

from __future__ import annotations

from collections.abc import Iterator

from .protocol import FRAME_SIZE, MAGIC, frame_ok


class StreamFramer:
    """Стан приймача одного каналу: недобрані байти й лічильник викинутих."""

    CAPACITY = 4 * FRAME_SIZE

    def __init__(self) -> None:
        self._buf = bytearray()
        self.resync_drops = 0
        self.frames_accepted = 0

    def feed(self, chunk: bytes) -> Iterator[bytes]:
        """Додає порцію з сокета й віддає всі кадри, що з неї склалися."""
        self._buf.extend(chunk)

        # Стеля буфера: якщо в каналі саме́ сміття, воно не має рости без меж.
        if len(self._buf) > self.CAPACITY:
            excess = len(self._buf) - self.CAPACITY
            self.resync_drops += excess
            del self._buf[:excess]

        while True:
            frame = self._next()
            if frame is None:
                return
            yield frame

    def _next(self) -> bytes | None:
        while True:
            start = self._buf.find(MAGIC)
            if start < 0:
                # Жодного синхробайта: увесь буфер — сміття.
                self.resync_drops += len(self._buf)
                self._buf.clear()
                return None
            if start > 0:
                self.resync_drops += start
                del self._buf[:start]

            if len(self._buf) < FRAME_SIZE:
                return None   # кадр іще не дійшов цілком

            candidate = bytes(self._buf[:FRAME_SIZE])
            if frame_ok(candidate):
                del self._buf[:FRAME_SIZE]
                self.frames_accepted += 1
                return candidate

            # 0xAA трапилася всередині даних побитого кадру — зсуваємо вікно на байт.
            self.resync_drops += 1
            del self._buf[:1]
