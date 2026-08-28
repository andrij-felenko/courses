#!/usr/bin/env python3
import asyncio
import os
import signal
import socket
import struct
import time
from typing import NamedTuple

# Константи протоколу телеметрії
FRAME_FORMAT = "!HHQffHH"
FRAME_SIZE = struct.calcsize(FRAME_FORMAT)  # 24 байти
MAGIC_HEADER = 0x544D                      # Сигнатура "TM"

class TelemetryRecord(NamedTuple):
    device_id: int
    timestamp_ms: int
    temperature: float
    voltage: float
    status_flags: int
    source_addr: str
    protocol: str

def calculate_checksum(data: bytes) -> int:
    """Обчислює 16-бітну контрольну суму XOR над послідовністю байтів."""
    cksum = 0
    for i in range(0, len(data), 2):
        val = (data[i] << 8) | (data[i + 1] if i + 1 < len(data) else 0)
        cksum ^= val
    return cksum & 0xFFFF

def parse_telemetry_frame(raw_data: bytes, source: str, proto: str) -> TelemetryRecord | None:
    """Виконує розбір та верифікацію цілісності бінарного кадру."""
    if len(raw_data) != FRAME_SIZE:
        return None

    magic, dev_id, ts, temp, volt, flags, cksum = struct.unpack(FRAME_FORMAT, raw_data)
    if magic != MAGIC_HEADER:
        return None

    expected_cksum = calculate_checksum(raw_data[:22])
    if cksum != expected_cksum:
        return None

    return TelemetryRecord(
        device_id=dev_id,
        timestamp_ms=ts,
        temperature=round(temp, 2),
        voltage=round(volt, 2),
        status_flags=flags,
        source_addr=source,
        protocol=proto,
    )

class TelemetryUDPProtocol(asyncio.DatagramProtocol):
    """Низькорівневий обробник дейтаграм без виділення проміжних задач Task."""

    def __init__(self, queue: asyncio.Queue[TelemetryRecord]) -> None:
        self.queue = queue
        self.transport: asyncio.DatagramTransport | None = None
        self.dropped_packets = 0

    def connection_made(self, transport: asyncio.BaseTransport) -> None:
        self.transport = transport  # type: ignore[assignment]

    def datagram_received(self, data: bytes, addr: tuple[str, int]) -> None:
        record = parse_telemetry_frame(data, f"{addr[0]}:{addr[1]}", "UDP")
        if record is not None:
            try:
                self.queue.put_nowait(record)
            except asyncio.QueueFull:
                self.dropped_packets += 1

    def error_received(self, exc: Exception) -> None:
        pass  # Мережеві збої окремих пакетів UDP ігноруються

class TelemetryServer:
    """Асинхронний сервер збирання та обробки телеметрії."""

    def __init__(
        self,
        host: str = "0.0.0.0",
        tcp_port: int = 9001,
        udp_port: int = 9002,
        max_conns: int = 1000,
        queue_size: int = 10000,
    ) -> None:
        self.host = host
        self.tcp_port = tcp_port
        self.udp_port = udp_port
        self.semaphore = asyncio.Semaphore(max_conns)
        self.queue: asyncio.Queue[TelemetryRecord] = asyncio.Queue(maxsize=queue_size)
        self.running = True
        self.records_processed = 0

    async def handle_tcp_client(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ) -> None:
        """Обробка потокового клієнтського TCP-з'єднання з контролем зворотного тиску."""
        peer = writer.get_extra_info("peername")
        peer_str = f"{peer[0]}:{peer[1]}" if peer else "unknown"

        # Обмежуємо кількість одночасних з'єднань
        async with self.semaphore:
            # Вимикаємо алгоритм Нейгла для мінімізації затримок ACK
            sock = writer.get_extra_info("socket")
            if sock and hasattr(socket, "TCP_NODELAY"):
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

            try:
                while self.running:
                    try:
                        raw_frame = await reader.readexactly(FRAME_SIZE)
                    except asyncio.IncompleteReadError:
                        break  # Клієнт коректно розірвав зв'язок

                    record = parse_telemetry_frame(raw_frame, peer_str, "TCP")
                    if record is None:
                        # Помилка формату — відправляємо 0xFF та закриваємо сесію
                        writer.write(b"\xFF")
                        await writer.drain()
                        break

                    # Додаємо запис у чергу обробки
                    await self.queue.put(record)

                    # Відправляємо однобайтний ACK (0x06) із синхронізацією drain()
                    writer.write(b"\x06")
                    await writer.drain()

            except (ConnectionResetError, BrokenPipeError):
                pass
            finally:
                writer.close()
                await writer.wait_closed()

    async def storage_worker(self, worker_id: int) -> None:
        """Фоновий воркер групового запису метрик у базу даних."""
        batch: list[TelemetryRecord] = []
        last_flush = time.monotonic()

        while self.running or not self.queue.empty():
            try:
                record = await asyncio.wait_for(self.queue.get(), timeout=0.1)
                batch.append(record)
                self.queue.task_done()
            except asyncio.TimeoutError:
                pass

            now = time.monotonic()
            if len(batch) >= 200 or (batch and now - last_flush >= 0.5):
                # Імітація пакетної вставки в ClickHouse / TimescaleDB
                self.records_processed += len(batch)
                batch.clear()
                last_flush = now

    async def run(self) -> None:
        """Головний цикл ініціалізації та структурованого виконання."""
        loop = asyncio.get_running_loop()

        # 1. Запуск TCP сервера з розширеною чергою backlog
        tcp_server = await asyncio.start_server(
            self.handle_tcp_client,
            self.host,
            self.tcp_port,
            reuse_address=True,
            backlog=2048,
        )

        # 2. Запуск UDP ендпоінта
        transport, protocol = await loop.create_datagram_endpoint(
            lambda: TelemetryUDPProtocol(self.queue),
            local_addr=(self.host, self.udp_port),
            reuse_port=hasattr(socket, "SO_REUSEPORT"),
        )

        # 3. Реєстрація сигналів коректного завершення
        stop_event = asyncio.Event()
        if os.name != "nt":
            for sig in (signal.SIGINT, signal.SIGTERM):
                loop.add_signal_handler(sig, stop_event.set)

        # 4. Структуроване керування фоновими задачами через TaskGroup
        try:
            async with asyncio.TaskGroup() as tg:
                # Створюємо 4 обчислювальні воркери
                for i in range(4):
                    tg.create_task(self.storage_worker(i))

                # Чекаємо сигналу зупинки від операційної системи
                await stop_event.wait()
                self.running = False

                # Зупиняємо приймання нових вхідних пакетів
                tcp_server.close()
                await tcp_server.wait_closed()
                transport.close()

                # Очікуємо повного вивантаження залишків черги
                await self.queue.join()

        except* Exception:
            pass  # Обробка аварійних винятків при завершенні

def main() -> None:
    server = TelemetryServer()
    asyncio.run(server.run())

if __name__ == "__main__":
    main()
