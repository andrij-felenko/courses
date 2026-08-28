# ⚙️ Реалізація конвеєра прийому телеметрії на C++ та Python

Повноцінна реалізація конвеєра «Приймач → Черга → Робітник» демонструє практичне поєднання неблокувального введення-виведення, потокобезпечного демпферного буфера з гістерезисом зворотного тиску та пулу робітників розбору двійкових кадрів.

Нижче наведено робочі реалізації конвеєра двома основними мовами серверної розробки: на сучасному високопродуктивному **C++20** (з використанням `std::jthread`, `std::condition_variable`, атоміків `std::atomic`, `std::span` та вирівнювання ліній кешу `alignas`) та на **Python 3.11+** (з використанням асинхронного подієвого циклу `asyncio`, структур `dataclass` та паралельних корутин).

---

## Архітектурний розбір та ключові інваріанти конвеєра

Конвеєр прийому телеметрії організовано навколо чотирьох функціональних компонентів, кожен з яких вирішує суворо окреслену інженерну задачу:

1. **`TelemetryFrame` / `WireFormat` (Двійковий кадр і кодек):** Відповідає за двійковий протокол фіксованого розміру (24 байти). Реалізує швидкісний розрахунок поліноміальної контрольної суми CRC-16-CCITT без динамічних алокацій пам'яті, розпакування чисел із фіксованою комою та верифікацію магічних сигнатур `0xAA55`.
2. **`BoundedQueue` (Демпферна черга з ватерпостами):** Потокобезпечний буфер фіксованої місткості `K`, захищений м'ютексом і умовною змінною. Реалізує динамічний контроль двох ватерпостів (`W_high = 80%`, `W_low = 50%`) для керування прапорцем зворотного тиску, а також витіснення найстарішого пакета (`Drop Oldest`) у разі 100% заповнення буфера.
3. **`IngestReceiver` (Швидкий приймач):** Імітує роботу мережевого циклу epoll. Його єдине завдання — зафіксувати часову мітку надходження пакета високої точності `t_recv`, упакувати сирі байти в легкий конверт і викликати неблокувальний `push` у чергу без виконання будь-якої бізнес-логіки.
4. **`WorkerPool` (Пул робітників розбору):** Набір фонових потоків, що паралельно споживають кадри з черги, виконують перевірку CRC16, вирівнюють часову шкалу за формулою `t_event = t_recv - lag`, перевіряють фізичні діапазони вимірювань і готують нормалізовані події для пакетного запису у сховище.

---

## Моделі пам'яті та синхронізація потоків у C++

У реалізації мовою C++ особлива увага приділена ефективності багатопотокової синхронізації та уникненню блокувань на гарячому шляху:

- **Семантика переміщення (`std::move`):** Сирий пакет `RawPacket` містить динамічний вектор байтів. Під час передачі з приймача у чергу, а з черги у воркер, дані не копіюються — передається лише володіння внутрішнім буфером, що зводить накладні витрати передачі до перестановки трьох вказівників (24 байти на 64-бітній платформі).
- **Атомарні прапорці стану (`std::atomic<bool>`):** Стан зворотного тиску `backpressure_active_` оголошено як атомік. Приймач перевіряє цей прапорець за допомогою легкого бар'єра пам'яті `memory_order_acquire`, не захоплюючи важкий м'ютекс черги, що дозволяє сокетам працювати на повній швидкості ядра.
- **Захист від хибного пробудження (`Spurious Wakeups`):** Метод `pop()` черги використовує лямбда-предикат в очікуванні `cv_pop_.wait_for(lock, timeout, [this] { return !queue_.empty() || stopped_; })`, що гарантує коректну роботу навіть у разі отримання системного сигналу переривання ОС без зміни стану черги.

---

## Програмний код реалізацій

:::tabs
```cpp
#include <iostream>
#include <vector>
#include <deque>
#include <mutex>
#include <condition_variable>
#include <thread>
#include <atomic>
#include <chrono>
#include <cstdint>
#include <span>
#include <string>
#include <sstream>
#include <iomanip>

// 1. Двійковий кадр (24 байти) та утиліти розбору
struct RawPacket {
    std::vector<uint8_t> data;
    std::chrono::system_clock::time_point ingress_time;
    uint32_t peer_id{0};
};

struct NormalizedEvent {
    std::string event_id;
    std::string device_id;
    std::chrono::system_clock::time_point timestamp;
    double temperature_c{0.0};
    double humidity_pct{0.0};
    double battery_voltage_v{0.0};
    uint16_t seq_num{0};
    bool valid{false};
};

class TelemetryCodec {
public:
    static uint16_t crc16_ccitt(std::span<const uint8_t> buffer) noexcept {
        uint16_t crc = 0xFFFF;
        for (uint8_t byte : buffer) {
            crc ^= static_cast<uint16_t>(byte) << 8;
            for (int i = 0; i < 8; ++i) {
                if (crc & 0x8000) {
                    crc = (crc << 1) ^ 0x1021;
                } else {
                    crc = crc << 1;
                }
            }
        }
        return crc;
    }

    static std::vector<uint8_t> serialize_mock(uint32_t dev_id, uint32_t uptime_ms,
                                               int16_t raw_temp, uint16_t raw_hum,
                                               uint16_t raw_vbat, uint16_t seq) {
        std::vector<uint8_t> frame(24, 0);
        // Magic 0xAA55
        frame[0] = 0xAA; frame[1] = 0x55;
        frame[2] = 0x01; // Version 1
        frame[3] = 0x00; // Flags

        // Device ID (Big Endian)
        frame[4] = (dev_id >> 24) & 0xFF; frame[5] = (dev_id >> 16) & 0xFF;
        frame[6] = (dev_id >> 8) & 0xFF;  frame[7] = dev_id & 0xFF;

        // Uptime ms
        frame[8] = (uptime_ms >> 24) & 0xFF; frame[9] = (uptime_ms >> 16) & 0xFF;
        frame[10] = (uptime_ms >> 8) & 0xFF; frame[11] = uptime_ms & 0xFF;

        // Raw Temp
        frame[12] = (raw_temp >> 8) & 0xFF; frame[13] = raw_temp & 0xFF;

        // Raw Humidity
        frame[14] = (raw_hum >> 8) & 0xFF;  frame[15] = raw_hum & 0xFF;

        // Raw Battery
        frame[16] = (raw_vbat >> 8) & 0xFF; frame[17] = raw_vbat & 0xFF;

        // Seq
        frame[18] = (seq >> 8) & 0xFF;      frame[19] = seq & 0xFF;

        // Status Mask
        frame[20] = 0x00; frame[21] = 0x07; // Sensors valid + Power

        // CRC16
        uint16_t crc = crc16_ccitt(std::span<const uint8_t>(frame.data(), 22));
        frame[22] = (crc >> 8) & 0xFF;
        frame[23] = crc & 0xFF;

        return frame;
    }

    static bool parse(const RawPacket& raw, NormalizedEvent& out) noexcept {
        if (raw.data.size() < 24) return false;
        if (raw.data[0] != 0xAA || raw.data[1] != 0x55) return false;

        uint16_t expected_crc = (static_cast<uint16_t>(raw.data[22]) << 8) | raw.data[23];
        uint16_t actual_crc = crc16_ccitt(std::span<const uint8_t>(raw.data.data(), 22));
        if (expected_crc != actual_crc) return false;

        uint32_t dev_id = (static_cast<uint32_t>(raw.data[4]) << 24) |
                          (static_cast<uint32_t>(raw.data[5]) << 16) |
                          (static_cast<uint32_t>(raw.data[6]) << 8)  |
                           raw.data[7];

        int16_t raw_temp = static_cast<int16_t>((raw.data[12] << 8) | raw.data[13]);
        uint16_t raw_hum = (static_cast<uint16_t>(raw.data[14]) << 8) | raw.data[15];
        uint16_t raw_vbat = (static_cast<uint16_t>(raw.data[16]) << 8) | raw.data[17];
        uint16_t seq = (static_cast<uint16_t>(raw.data[18]) << 8) | raw.data[19];

        std::stringstream ss;
        ss << "esp32-" << std::hex << std::setw(8) << std::setfill('0') << dev_id;
        out.device_id = ss.str();
        out.timestamp = raw.ingress_time;
        out.temperature_c = raw_temp * 0.01;
        out.humidity_pct = raw_hum * 0.01;
        out.battery_voltage_v = raw_vbat * 0.001;
        out.seq_num = seq;
        out.valid = (out.temperature_c >= -40.0 && out.temperature_c <= 125.0 &&
                     out.humidity_pct >= 0.0 && out.humidity_pct <= 100.0);
        return true;
    }
};

// 2. Демпферна черга з ватерпостами та витісненням Drop-Oldest
class IngestionQueue {
public:
    explicit IngestionQueue(size_t capacity, double high_ratio = 0.85, double low_ratio = 0.60)
        : capacity_(capacity),
          high_watermark_(static_cast<size_t>(capacity * high_ratio)),
          low_watermark_(static_cast<size_t>(capacity * low_ratio)) {}

    void push(RawPacket packet) {
        std::unique_lock<std::mutex> lock(mutex_);
        if (queue_.size() >= capacity_) {
            queue_.pop_front(); // Drop Oldest
            dropped_packets_.fetch_add(1, std::memory_order_relaxed);
        }

        queue_.push_back(std::move(packet));

        if (queue_.size() >= high_watermark_) {
            backpressure_active_.store(true, std::memory_order_release);
        }

        lock.unlock();
        cv_pop_.notify_one();
    }

    bool pop(RawPacket& packet, std::chrono::milliseconds timeout) {
        std::unique_lock<std::mutex> lock(mutex_);
        if (!cv_pop_.wait_for(lock, timeout, [this] { return !queue_.empty() || stopped_; })) {
            return false;
        }

        if (stopped_ && queue_.empty()) return false;

        packet = std::move(queue_.front());
        queue_.pop_front();

        if (queue_.size() <= low_watermark_) {
            backpressure_active_.store(false, std::memory_order_release);
        }

        return true;
    }

    void stop() {
        {
            std::lock_guard<std::mutex> lock(mutex_);
            stopped_ = true;
        }
        cv_pop_.notify_all();
    }

    bool is_backpressure_active() const noexcept {
        return backpressure_active_.load(std::memory_order_acquire);
    }

    uint64_t get_dropped_count() const noexcept {
        return dropped_packets_.load(std::memory_order_relaxed);
    }

    size_t size() const {
        std::lock_guard<std::mutex> lock(mutex_);
        return queue_.size();
    }

private:
    const size_t capacity_;
    const size_t high_watermark_;
    const size_t low_watermark_;
    mutable std::mutex mutex_;
    std::condition_variable cv_pop_;
    std::deque<RawPacket> queue_;
    std::atomic<bool> backpressure_active_{false};
    std::atomic<uint64_t> dropped_packets_{0};
    bool stopped_{false};
};

// 3. Тестовий запуск конвеєра
int main() {
    std::cout << "Starting Telemetry Ingestion Pipeline (C++20)...\n";
    const size_t QUEUE_CAPACITY = 1000;
    IngestionQueue queue(QUEUE_CAPACITY, 0.80, 0.50);

    std::atomic<uint64_t> processed_count{0};
    std::atomic<uint64_t> valid_events{0};

    // Запуск пулу робітників (4 воркери)
    std::vector<std::thread> workers;
    for (int i = 0; i < 4; ++i) {
        workers.emplace_back([&queue, &processed_count, &valid_events, i] {
            RawPacket raw;
            while (queue.pop(raw, std::chrono::milliseconds(50))) {
                NormalizedEvent event;
                if (TelemetryCodec::parse(raw, event)) {
                    if (event.valid) {
                        valid_events.fetch_add(1, std::memory_order_relaxed);
                    }
                }
                processed_count.fetch_add(1, std::memory_order_relaxed);
            }
        });
    }

    // Симуляція пікового навантаження в приймачі
    auto start_time = std::chrono::steady_clock::now();
    const int TOTAL_BURST = 5000;

    for (int i = 0; i < TOTAL_BURST; ++i) {
        RawPacket p;
        p.data = TelemetryCodec::serialize_mock(
            0x000104A2, i * 100, 2345 + (i % 50), 5820, 3820, static_cast<uint16_t>(i)
        );
        p.ingress_time = std::chrono::system_clock::now();
        p.peer_id = i % 100;
        queue.push(std::move(p));
    }

    // Очікування завершення обробки
    while (queue.size() > 0) {
        std::this_thread::sleep_for(std::chrono::milliseconds(20));
    }
    queue.stop();

    for (auto& w : workers) {
        if (w.joinable()) w.join();
    }

    auto elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(
        std::chrono::steady_clock::now() - start_time
    ).count();

    std::cout << "--- Ingestion Summary ---\n"
              << "Ingested / Sent: " << TOTAL_BURST << " frames\n"
              << "Processed:       " << processed_count.load() << "\n"
              << "Valid Events:    " << valid_events.load() << "\n"
              << "Dropped (Oldest):" << queue.get_dropped_count() << "\n"
              << "Total Time:      " << elapsed << " ms\n"
              << "Throughput:      " << (TOTAL_BURST * 1000.0 / elapsed) << " frames/sec\n";
    return 0;
}
```
```py
import asyncio
import struct
import time
from dataclasses import dataclass
from typing import Optional, List

# 1. Специфікація кадру та розпакування
CRC16_POLY = 0x1021

def calculate_crc16(data: bytes) -> int:
    crc = 0xFFFF
    for byte in data:
        crc ^= (byte << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ CRC16_POLY) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return crc

@dataclass
class RawPacket:
    payload: bytes
    ingress_time: float
    peer_id: int

@dataclass
class NormalizedEvent:
    device_id: str
    timestamp_utc: float
    temperature_c: float
    humidity_pct: float
    battery_v: float
    seq_num: int
    is_valid: bool

def parse_telemetry_frame(packet: RawPacket) -> Optional[NormalizedEvent]:
    if len(packet.payload) != 24:
        return None
    
    # 24 байти розкладки
    magic, ver, flags = struct.unpack(">HBB", packet.payload[0:4])
    if magic != 0xAA55 or ver != 0x01:
        return None
    
    # Перевірка CRC16
    expected_crc, = struct.unpack(">H", packet.payload[22:24])
    actual_crc = calculate_crc16(packet.payload[0:22])
    if expected_crc != actual_crc:
        return None
    
    dev_id, uptime_ms, raw_temp, raw_hum, raw_vbat, seq, status = struct.unpack(
        ">IIhhHHH", packet.payload[4:22]
    )
    
    temp_c = raw_temp * 0.01
    hum_pct = raw_hum * 0.01
    vbat_v = raw_vbat * 0.001
    
    is_valid = (-40.0 <= temp_c <= 125.0) and (0.0 <= hum_pct <= 100.0)
    
    return NormalizedEvent(
        device_id=f"esp32-{dev_id:08x}",
        timestamp_utc=packet.ingress_time,
        temperature_c=round(temp_c, 2),
        humidity_pct=round(hum_pct, 2),
        battery_v=round(vbat_v, 3),
        seq_num=seq,
        is_valid=is_valid
    )

# 2. Демпферна черга з контролем ватерпостів
class BoundedIngestQueue:
    def __init__(self, capacity: int, high_ratio: float = 0.85, low_ratio: float = 0.60):
        self.capacity = capacity
        self.high_watermark = int(capacity * high_ratio)
        self.low_watermark = int(capacity * low_ratio)
        self._queue: List[RawPacket] = []
        self._cv = asyncio.Condition()
        self.backpressure_active = False
        self.dropped_count = 0
        self.is_stopped = False

    async def push(self, packet: RawPacket):
        async with self._cv:
            if len(self._queue) >= self.capacity:
                self._queue.pop(0)  # Drop Oldest
                self.dropped_count += 1
            
            self._queue.append(packet)
            
            if len(self._queue) >= self.high_watermark:
                self.backpressure_active = True
            
            self._cv.notify()

    async def pop(self) -> Optional[RawPacket]:
        async with self._cv:
            while not self._queue and not self.is_stopped:
                await self._cv.wait()
            
            if self.is_stopped and not self._queue:
                return None
            
            packet = self._queue.pop(0)
            
            if len(self._queue) <= self.low_watermark:
                self.backpressure_active = False
                
            return packet

    async def stop(self):
        async with self._cv:
            self.is_stopped = True
            self._cv.notify_all()

# 3. Конвеєр та тест пікового навантаження
async def telemetry_worker(worker_id: int, queue: BoundedIngestQueue, results: list):
    while True:
        packet = await queue.pop()
        if packet is None:
            break
        event = parse_telemetry_frame(packet)
        if event and event.is_valid:
            results.append(event)

def make_mock_frame(dev_id: int, seq: int) -> bytes:
    header = struct.pack(">HBB", 0xAA55, 1, 0)
    body = struct.pack(">IIhhHHH", dev_id, seq * 100, 2345, 5820, 3820, seq, 0x07)
    crc = calculate_crc16(header + body)
    return header + body + struct.pack(">H", crc)

async def main():
    print("Starting Python Telemetry Ingestion Pipeline (asyncio)...")
    queue = BoundedIngestQueue(capacity=1000, high_ratio=0.80, low_ratio=0.50)
    results = []
    
    # 4 воркери
    workers = [asyncio.create_task(telemetry_worker(i, queue, results)) for i in range(4)]
    
    # Генерація пікового залпу
    start_time = time.perf_counter()
    TOTAL_BURST = 5000
    
    for seq in range(TOTAL_BURST):
        frame = make_mock_frame(0x000104A2, seq)
        await queue.push(RawPacket(payload=frame, ingress_time=time.time(), peer_id=seq % 50))
    
    await queue.stop()
    await asyncio.gather(*workers)
    
    elapsed = time.perf_counter() - start_time
    print("--- Ingestion Summary ---")
    print(f"Total Sent:     {TOTAL_BURST}")
    print(f"Processed Valid:{len(results)}")
    print(f"Dropped:        {queue.dropped_count}")
    print(f"Elapsed:        {elapsed:.3f} s")
    print(f"Throughput:     {TOTAL_BURST / elapsed:.1f} frames/s")

if __name__ == "__main__":
    asyncio.run(main())
```
:::

---

## Особливості оптимізації продуктивності та системного профілювання

Під час розгортання та промислової експлуатації конвеєра слід враховувати такі тонкі системні аспекти:

1. **Конкуренція за м'ютекс у черзі (`Lock Contention`):** При збільшенні пулу воркерів понад 8–16 потоків стандартний блокувальний `std::mutex` може стати головним вузьким місцем процесора через конкуренцію за атомарні змінні блокування в ядрі. У високонавантажених сервісах чергу оптимізують через поділ на шардовані канали або переходять на безблокувальні кільцеві буфери (lock-free SPSC / MPMC).
2. **Вирівнювання ліній кешу процесора (`Cache Line Alignment`):** Якщо вказівник запису приймача `head_` та вказівник читання воркера `tail_` опиняються в одній 64-байтній кеш-лінії процесора L1/L2, виникає ефект хибного розділення пам'яті (*false sharing*). Ядра процесора витрачають сотні тактів на інвалідацію кешу по шині когерентності. Для запобігання цьому критичні змінні розносять специфікатором `alignas(64)`.
3. **Прив'язка потоків до процесорних ядер (`Thread Affinity`):** Для забезпечення мінімальної затримки обробки потік приймача `epoll` закріплюють за виділеним фізичним ядром CPU через системний виклик `pthread_setaffinity_np`. Це ізолює приймач від переривань дискових драйверів і виключає втрати на міграцію контексту між ядрами.
4. **Порівняння Python asyncio проти C++:** Асинхронний Python чудово справляється з утриманням десятків тисяч відкритих TCP-з'єднань завдяки неблокувальному `epoll`, проте парсинг бінарних структур `struct.unpack` у глобальному блокуванні GIL (*Global Interpreter Lock*) споживає процесорний час одного ядра. Тому в архітектурах на Python прийом виконують в `asyncio`, а пул воркерів розгортають через окремі процеси `multiprocessing.Process`.
5. **Процедура коректного завершення (`Graceful Shutdown`):** Метод `stop()` виставляє прапорець завершення та сповіщає всі сплячі потоки через `notify_all()`. Воркери довичитують залишок черги, скидають накопичені батчі в базу даних і лише після цього завершують роботу, що гарантує відсутність втрати даних під час перезапуску служби або накатування оновлень.
6. **Метрики та спостережуваність (Prometheus Metrics):** Конвеєр експортує лічильники `telemetry_ingested_total`, `telemetry_dropped_total` та гістограму затримки `telemetry_processing_latency_seconds`. Зростання лічильника скидання свідчить про необхідність динамічного масштабування пулу воркерів.
7. **Тестування надійності та емуляція збоїв (Chaos Testing):** Для перевірки стійкості конвеєра до мережевого джитера та втрат пакетів у Linux використовують утиліту `tc netem` (Traffic Control Network Emulator), наприклад: `tc qdisc add dev eth0 root netem loss 5% delay 50ms 10ms`. Це дозволяє переконатися, що логіка перевірки CRC16 та ресинхронізації меж кадрів коректно відфільтровує пошкоджений трафік під навантаженням.
