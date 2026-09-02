"""Пошук кадрів у байтовому потоці.

Схема розбирає ГОТОВИЙ кадр. Звідки він починається в потоці з UART, де
між пакетами трапляється шум, а сам пакет приходить трьома шматками, —
питання не до схеми.

Ключове рішення: після невдачі викидаємо ОДИН байт, а не весь буфер.
Справжній SOF цілком може стояти всередині щойно відкинутого сміття, і
жадібне очищення буфера коштувало б наступного кадру.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import BinaryIO, Iterator

from .crc import crc16_ccitt, crc_input
from .wire import EOF, FOOTER_LEN, HEADER_LEN, MAX_PAYLOAD, SOF


@dataclass(slots=True)
class FramerStats:
    """Лічильники здоров'я каналу — те, що йде в метрики шлюзу."""

    bytes_in: int = 0
    frames: int = 0
    dropped: int = 0  # байтів викинуто як сміття
    resyncs: int = 0  # разів довелося шукати межу кадру наново
    bad_len: int = 0
    bad_eof: int = 0
    bad_crc: int = 0

    def as_dict(self) -> dict[str, int]:
        return {
            "bytes_in": self.bytes_in,
            "frames": self.frames,
            "dropped": self.dropped,
            "resyncs": self.resyncs,
            "bad_len": self.bad_len,
            "bad_eof": self.bad_eof,
            "bad_crc": self.bad_crc,
        }


@dataclass(slots=True)
class FrameReader:
    """Автомат станів, що витягає з потоку цілі перевірені кадри."""

    max_payload: int = MAX_PAYLOAD
    stats: FramerStats = field(default_factory=FramerStats)
    _buf: bytearray = field(default_factory=bytearray, repr=False)

    def __post_init__(self) -> None:
        if not 0 <= self.max_payload <= 0xFFFF:
            raise ValueError(f"max_payload={self.max_payload} поза межами поля u2")

    @property
    def pending(self) -> int:
        """Скільки байтів чекає на добір решти кадру."""
        return len(self._buf)

    def reset(self) -> None:
        """Порт перевідкрили — недобраний хвіст більше ні до чого."""
        self.stats.dropped += len(self._buf)
        self._buf.clear()

    def feed(self, chunk: bytes | bytearray) -> list[bytes]:
        """Додає шматок потоку й повертає всі кадри, що з нього склалися."""
        self._buf += chunk
        self.stats.bytes_in += len(chunk)
        return self._extract()

    def _drop(self, count: int) -> None:
        del self._buf[:count]
        self.stats.dropped += count

    def _resync(self) -> None:
        self._drop(1)
        self.stats.resyncs += 1

    def _extract(self) -> list[bytes]:
        found: list[bytes] = []
        while self._buf:
            if self._buf[0] != SOF:
                at = self._buf.find(SOF)
                if at < 0:
                    self._drop(len(self._buf))  # у буфері самий шум
                    break
                self._drop(at)
                continue

            if len(self._buf) < HEADER_LEN:
                break  # заголовок ще не доїхав

            declared = int.from_bytes(self._buf[4:6], "little")
            if declared > self.max_payload:
                # Це не наш заголовок, а збіг: байт 0xAA всередині шуму.
                self.stats.bad_len += 1
                self._resync()
                continue

            total = HEADER_LEN + declared + FOOTER_LEN
            if len(self._buf) < total:
                break  # кадр цілий, але ще не весь тут

            candidate = bytes(self._buf[:total])
            if candidate[-1] != EOF:
                self.stats.bad_eof += 1
                self._resync()
                continue

            written = int.from_bytes(candidate[HEADER_LEN + declared :][:2], "little")
            if written != crc16_ccitt(crc_input(candidate, declared)):
                self.stats.bad_crc += 1
                self._resync()
                continue

            del self._buf[:total]
            self.stats.frames += 1
            found.append(candidate)
        return found


def read_frames(
    reader: FrameReader, source: BinaryIO, *, chunk_size: int = 64
) -> Iterator[bytes]:
    """Гонить потік крізь рамкувальник, віддаючи кадри в міру появи."""
    while chunk := source.read(chunk_size):
        yield from reader.feed(chunk)
