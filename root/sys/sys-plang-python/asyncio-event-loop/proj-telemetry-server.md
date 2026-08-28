# ⚙️ Високонавантажений сервер телеметрії на TCP та UDP

У сучасних розподілених системах моніторингу інтернету речей (IoT), промислової автоматики та телематики транспортних засобів сервери збирання даних стикаються з двома діаметрально протилежними вимогами до мережевої підсистеми:
1. **Низька затримка для потокових вимірювань (UDP):** Датчики транслюють метрики з високою частотою (10–100 Гц). Втрата окремого пакета не є критичною, однак накладні витрати на підтвердження доставки TCP-сесій та встановлення рукостискань (Handshake) перевантажують мережеву інфраструктуру.
2. **Гарантована доставка та двостороннє керування (TCP):** Контролери вимагають надійного підтвердження отримання пакетів, передачі критичних сигналів тривоги та можливості віддаленої конфігурації через стійке з'єднання.

Нижче наведено промисловий зразок високопродуктивного асинхронного сервера на базі Python `asyncio`, що одночасно обслуговує UDP-потоки та TCP-сесії, застосовуючи структуровану асинхронність `TaskGroup`, контроль зворотного тиску (*backpressure*), обмеження пулу з'єднань через `Semaphore` та безпечну обробку системних сигналів завершення роботи.

---

## 1. Архітектура та формат бінарного кадру

Використання текстових форматів серіалізації (JSON, XML або CSV) у високонавантажених серверах телеметрії призводить до неконтрольованого виділення пам'яті в купі Python, фрагментації буферів рядків та частих пауз збирача сміття (GC).

Для мінімізації накладних витрат у системі застосовується компактний 24-байтовий бінарний кадр фіксованої довжини:

| Зсув (байти) | Поле | Формат struct | Розмір | Призначення |
|---|---|---|---|---|
| `0..1` | `magic` | `!H` (uint16) | 2 байти | Сигнатура протоколу (`0x544D` — ASCII 'TM') |
| `2..3` | `device_id` | `!H` (uint16) | 2 байти | Унікальний числовий ідентифікатор пристрою (0–65535) |
| `4..11` | `timestamp_ms` | `!Q` (uint64) | 8 байтів | Епохальна часова мітка Unix у мілісекундах |
| `12..15` | `temperature` | `!f` (float32) | 4 байти | Значення температури сенсора у градусах Цельсія |
| `16..19` | `voltage` | `!f` (float32) | 4 байти | Напруга живлення вузла у вольтах |
| `20..21` | `status_flags` | `!H` (uint16) | 2 байти | Бітова маска стану (0x01: аварія, 0x02: низький заряд) |
| `22..23` | `checksum` | `!H` (uint16) | 2 байти | Контрольна сума XOR для верифікації цілісності даних |

Рядок форматування `!HHQffHH` у модулі `struct` задає мережевий порядок байтів Big-Endian, що гарантує сумісність між різними апаратними архітектурами (ARM, RISC-V, x86).

---

## 2. Повна реалізація асинхронного сервера телеметрії

```python
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
```

---

## 3. Детальний аналіз інженерних рішень і пасток

### 1. Управління алокаціями в UDP: Чому не варто створювати Task на кожен пакет

Найпоширеніша помилка при роботі з асинхронним UDP — виклик `asyncio.create_task(process_packet(data))` всередині методу `datagram_received()`. Кожен створений екземпляр `Task` є повноцінним Python-об'єктом, що виділяє пам'ять у купі інтерпретатора, створює контекст виконання `contextvars` та додає дію в чергу `_ready`.

При інтенсивності вхідного потоку 50 000 пакетів на секунду інтерпретатор витрачає понад 70% процесорного часу виключно на ініціалізацію та знищення структур `Task`. Протокол `TelemetryUDPProtocol` вирішує цю проблему за допомогою прямої передачі розібраного кадру у чергу `asyncio.Queue` через неблокувальний метод `put_nowait()`. Це усуває накладні витрати й дозволяє одному потоку Python обробляти екстремальні обсяги UDP-трафіку.

### 2. Захист від переповнення пам'яті через обмежені черги (Bounded Queues)

Якщо база даних або аналітичне сховище уповільнює запис (наприклад, під час періодичного скидання журналів на диск), черга між мережевими приймачами та воркерами починає неконтрольовано зростати. Якщо черга необмежена (`maxsize=0`), це неминуче призводить до аварійного завершення процесу системним захисником пам'яті (*Out-Of-Memory Killer*, OOM).

Встановлення параметра `asyncio.Queue(maxsize=10000)` реалізує чіткі інженерні гарантії:
- **Для UDP-протоколу:** Застосовується стратегія скидання пакетів (*Load Shedding*). При переповненні черги метод `put_nowait()` генерує виняток `asyncio.QueueFull`, лічильник втрат інкрементується, а процес зберігає стабільний обсяг резидентної пам'яті (RSS).
- **Для TCP-протоколу:** Виклик `await self.queue.put(record)` призупиняє виконання корутини конкретного клієнта. Оскільки корутина зупиняється на `put`, вона припиняє читати з сокета через `readexactly()`. Вхідний буфер сокета операційної системи заповнюється, і стек TCP автоматично зменшує розмір вікна прийому (*TCP Receive Window*, `win`), сигналізуючи клієнтові про необхідність сповільнити передачу.

### 3. Обов'язковість виклику writer.drain() у TCP-обробниках

Метод `writer.write()` у класі `StreamWriter` є повністю неблокувальним і лише додає байти до внутрішнього буфера транспорту. Якщо сервер надсилає відповіді повільному клієнту або у нестабільній мобільній мережі без виклику `await writer.drain()`, розмір вихідного буфера в оперативній пам'яті може зростати до сотень мегабайтів.

Виклик `await writer.drain()` активує механізм зворотного тиску: якщо буфер перевищив поріг `high_water` (за замовчуванням 64 КБ), поточна корутина призупиняється і не виконує подальших дій доти, доки операційна система не вивантажить сокетний буфер у фізичну мережу нижче порогу `low_water` (16 КБ).

### 4. Налаштування низькорівневих параметрів сокетів

Для досягнення мінімальних затримок відгуку сервер застосовує оптимізаційні системні прапорці:
- **`TCP_NODELAY`:** Вимикає алгоритм Нейгла, змушуючи операційну систему відправляти 1-байтний ACK-пакет негайно, не очікуючи накопичення повного TCP-сегмента (MSS). Це скорочує затримку підтвердження від 40–200 мс до часток мілісекунди.
- **`SO_REUSEADDR` та `SO_REUSEPORT`:** Дозволяють серверу миттєво перезапускатися без зависання сокета у стані `TIME_WAIT`, а також підтримують запуск кількох паралельних процесів сервера на одному мережевому порту для масштабування на всі ядра процесора.
- **`SO_RCVBUF` (Системний сокетний буфер прийому):** При роботі з високошвидкісними UDP-потоками системний розмір буфера прийому за замовчуванням (зазвичай 212 КБ у Linux) може переповнюватися під час короткочасних сплесків. Збільшення розміру буфера через `sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 4 * 1024 * 1024)` запобігає апаратним втратам пакетів на рівні мережевого драйвера ядра до їх зчитування циклом подій.

### 5. Порядок коректного завершення роботи (Graceful Shutdown)

Асинхронний сервер не повинен обривати активні транзакції під час отримання сигналів завершення `SIGTERM` або `SIGINT`. Послідовність зупинки реалізована у чотири детерміновані кроки:
1. **Зупинка вхідного трафіку:** Виклики `tcp_server.close()` та `transport.close()` закривають слухаючі дескриптори. Нові підключення перестають прийматися, проте вже відкриті TCP-сесії продовжують оброблятися.
2. **Переведення прапорця `self.running = False`:** Клієнтські цикли завершують поточні кадри та штатно закривають з'єднання.
3. **Очищення черги повідомлень через `await self.queue.join()`:** Цикл очікує, поки воркери вичитають і збережуть усі накопичені кадри.
4. **Автоматичне згортання пулу через `TaskGroup`:** При виході з блоку `async with asyncio.TaskGroup()` усі фонові воркери гарантовано завершуються без витоків задач у пам'яті.
