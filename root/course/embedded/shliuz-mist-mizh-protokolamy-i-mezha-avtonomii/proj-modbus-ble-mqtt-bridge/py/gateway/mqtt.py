"""Мінімальний клієнт MQTT 3.1.1: CONNECT, PUBLISH з QoS 1, PINGREQ, DISCONNECT.

QoS 1 тут не примха: черга віддає повідомлення лише після PUBACK, тож обрив у
момент передавання коштує повтору, а не втраченого вимірювання.

На відміну від версії на C, де відповіді вичитує та сама задача, що й публікує,
тут працюють дві фонові корутини: одна читає сокет і роздає підтвердження за
номерами пакетів, друга тримає keep-alive. Публікація просто чекає на свою
обіцянку.

На виробництві сокет обгортають у TLS (``ssl=`` в ``open_connection``); рамка
пакетів від цього не міняється, тому тут чистий TCP — щоб було видно кадри.
"""

from __future__ import annotations

import asyncio
import socket
import struct

CONNECT = 0x10
CONNACK = 0x20
PUBLISH = 0x30
PUBACK = 0x40
PINGREQ = 0xC0
PINGRESP = 0xD0
DISCONNECT = 0xE0

MAX_PACKET = 1024
ACK_TIMEOUT = 5.0


class MqttError(Exception):
    """Канал до брокера зламався або брокер відмовив."""


def _encode_remaining(length: int) -> bytes:
    """Довжина решти пакета — змінне ціле по 7 біт на байт, старший біт «є ще»."""
    out = bytearray()
    while True:
        byte = length % 128
        length //= 128
        out.append(byte | 0x80 if length else byte)
        if not length:
            return bytes(out)


def _encode_string(text: str) -> bytes:
    raw = text.encode()
    return struct.pack(">H", len(raw)) + raw


async def _read_packet(reader: asyncio.StreamReader) -> tuple[int, bytes]:
    header = await reader.readexactly(1)
    remaining, multiplier = 0, 1
    for attempt in range(4):
        byte = (await reader.readexactly(1))[0]
        remaining += (byte & 0x7F) * multiplier
        if not byte & 0x80:
            break
        multiplier *= 128
        if attempt == 3:
            raise MqttError("довжина понад чотири байти — потік зіпсовано")
    if remaining > MAX_PACKET:
        raise MqttError(f"пакет на {remaining} байтів завеликий")
    payload = await reader.readexactly(remaining) if remaining else b""
    return header[0] & 0xF0, payload


class MqttClient:
    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter,
                 keepalive: int) -> None:
        self._reader = reader
        self._writer = writer
        self._keepalive = keepalive
        self._next_id = 1
        self._pending: dict[int, asyncio.Future[None]] = {}
        self._pong = asyncio.Event()
        self._failure: MqttError | None = None
        self._read_task = asyncio.create_task(self._read_loop())
        self._ping_task = asyncio.create_task(self._ping_loop())

    @classmethod
    async def connect(cls, host: str, port: int, client_id: str, keepalive: int = 30,
                      timeout: float = 5.0) -> MqttClient:
        try:
            reader, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout)
        except (OSError, asyncio.TimeoutError) as error:
            raise MqttError(f"до {host}:{port} не достукатися ({error})") from error

        # Телеметрія — короткі пакети; затримка Nagle тут лише псує реакцію.
        raw_socket = writer.get_extra_info("socket")
        if raw_socket is not None:
            raw_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        body = (_encode_string("MQTT")
                + bytes([0x04,   # рівень протоколу 4 = MQTT 3.1.1
                         0x02])  # clean session: черга живе в нас, а не в брокері
                + struct.pack(">H", keepalive)
                + _encode_string(client_id))
        writer.write(bytes([CONNECT]) + _encode_remaining(len(body)) + body)
        await writer.drain()

        try:
            packet_type, payload = await asyncio.wait_for(_read_packet(reader), ACK_TIMEOUT)
        except (asyncio.IncompleteReadError, asyncio.TimeoutError, OSError) as error:
            writer.close()
            raise MqttError(f"брокер не відповів на CONNECT ({error})") from error

        if packet_type != CONNACK or len(payload) < 2 or payload[1] != 0x00:
            writer.close()
            code = payload[1] if len(payload) >= 2 else 0xFF
            # 0x04 — хибні дані входу, 0x05 — не авторизовано.
            raise MqttError(f"брокер відмовив, код 0x{code:02X}")

        return cls(reader, writer, keepalive)

    async def _read_loop(self) -> None:
        try:
            while True:
                packet_type, payload = await _read_packet(self._reader)
                if packet_type == PUBACK and len(payload) >= 2:
                    packet_id = struct.unpack(">H", payload[:2])[0]
                    future = self._pending.pop(packet_id, None)
                    if future is not None and not future.done():
                        future.set_result(None)
                elif packet_type == PINGRESP:
                    self._pong.set()
                # Чужі пакети мовчки ковтаємо: ми ні на що не підписані.
        except asyncio.CancelledError:
            raise
        except Exception as error:  # обрив, скидання, зіпсований потік
            self._fail(MqttError(f"канал до брокера зламався ({error})"))

    async def _ping_loop(self) -> None:
        try:
            while True:
                await asyncio.sleep(self._keepalive / 2)
                self._pong.clear()
                self._writer.write(bytes([PINGREQ, 0x00]))
                await self._writer.drain()
                try:
                    await asyncio.wait_for(self._pong.wait(), ACK_TIMEOUT)
                except asyncio.TimeoutError:
                    # Мовчання у відповідь — єдина ознака мертвого каналу, яку ми
                    # маємо: TCP-сокет вважатиметься живим ще довгі хвилини.
                    self._fail(MqttError("брокер не відповів на PINGREQ"))
                    return
        except asyncio.CancelledError:
            raise
        except OSError as error:
            self._fail(MqttError(f"PINGREQ не пішов ({error})"))

    def _fail(self, error: MqttError) -> None:
        if self._failure is None:
            self._failure = error
        for future in self._pending.values():
            if not future.done():
                future.set_exception(error)
        self._pending.clear()
        self._writer.close()

    async def publish_qos1(self, topic: str, payload: str) -> None:
        if self._failure is not None:
            raise self._failure

        packet_id = self._next_id
        self._next_id = self._next_id % 0xFFFF + 1  # нуль як ідентифікатор заборонено

        body = _encode_string(topic) + struct.pack(">H", packet_id) + payload.encode()
        packet = bytes([PUBLISH | 0x02]) + _encode_remaining(len(body)) + body  # QoS 1

        future: asyncio.Future[None] = asyncio.get_running_loop().create_future()
        self._pending[packet_id] = future
        try:
            self._writer.write(packet)
            await self._writer.drain()
            await asyncio.wait_for(future, ACK_TIMEOUT)
        except asyncio.TimeoutError as error:
            self._pending.pop(packet_id, None)
            raise MqttError(f"брокер не підтвердив пакет {packet_id}") from error
        except OSError as error:
            self._pending.pop(packet_id, None)
            raise MqttError(f"публікація не пішла ({error})") from error

    async def close(self) -> None:
        for task in (self._read_task, self._ping_task):
            task.cancel()
        await asyncio.gather(self._read_task, self._ping_task, return_exceptions=True)
        if self._failure is None:
            try:
                self._writer.write(bytes([DISCONNECT, 0x00]))
                await self._writer.drain()
            except OSError:
                pass  # прощання — ввічливість, а не обов'язок
        self._writer.close()
        try:
            await self._writer.wait_closed()
        except OSError:
            pass

    async def __aenter__(self) -> MqttClient:
        return self

    async def __aexit__(self, *_exc_info: object) -> None:
        await self.close()
