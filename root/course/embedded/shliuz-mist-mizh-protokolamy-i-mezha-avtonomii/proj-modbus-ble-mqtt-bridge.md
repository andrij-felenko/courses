# ⚙️ Програмний міст Modbus/BLE-to-MQTT з локальною автономією та буфером Store-and-Forward

Цей проєкт реалізує архітектурне ядро промислового IoT-шлюзу, який об'єднує два принципово різних фізичних середовища (дротову польову шину RS-485 з протоколом Modbus RTU та бездротовий сенсорний інтерфейс BLE GATT) із хмарною аналітичною платформою через брокер MQTT. Головна інженерна вимога до цієї підсистеми — повна відмовостійкість: за умов нестабільного, періодичного або повністю обірваного стільникового/оптичного інтернет-каналу (WAN) шлюз зобов'язаний зберігати локальну працездатність, не втрачати жодного вимірювання й виконувати аварійні процедури автономно, без очікування директив із центрального сервера.

### Постановка задачі та декомпозиція потоків виконання

Шлюз виступає активним координатором усього локального сегмента обладнання. Програмний конвеєр розділено на чотири асинхронні задачі (потоки виконання в ОС або корутини в середовищі `asyncio`), ізольовані одна від одної за допомогою потокобезпечних черг обміну повідомленнями:

1. **Низхідний опитувач польових шин (Southbound Poller Task):**
   * Періодично формує та відправляє у послідовний порт RS-485 двійкові запити Modbus RTU (Master Mode). Для нашого прикладу опитується підлеглий котел або датчик тиску (Slave ID = 1, функція 03 `Read Holding Registers`, початковий регістр 0x0001, кількість регістрів — 2). Отримані два 16-бітні регістри склеюються у 32-бітне число з рухомою комою відповідно до стандарту IEEE 754.
   * Паралельно приймає бездротові пакети сповіщень (GATT Notifications) або рекламні кадри (BLE Advertising) від вібродавачів і термометрів на рухомих підшипниках, розпаковуючи шістнадцяткові байти у фізичні значення температури в градусах Цельсія.
2. **Локальний супервізор безпеки (Edge Autonomy Rule Engine):**
   * Миттєво перевіряє отримані фізичні значення на відповідність технологічним картам безпеки. Якщо виміряний тиск у системі перевищує критичний поріг (10.0 бар), супервізор не витрачає час на мережевий запит до хмари (який може затриматися на секунди або взагалі впасти по таймауту). Він негайно формує пряму команду аварійного скидання (Modbus Function 05 `Write Single Coil`, адреса 0x0010 = ON) і відправляє її безпосередньо у польову шину з найвищим пріоритетом.
3. **Енергонезалежний буфер Store-and-Forward:**
   * У нормальному стані, коли TLS-з'єднання з MQTT-брокером активне, повідомлення негайно серіалізуються та передаються в сокет.
   * Якщо канал WAN обірвано (таймаут TCP Keep-Alive, відсутність відповіді на `PINGREQ`), вихідні повідомлення перенаправляються у циклічний буфер (Ring Buffer). Буфер реалізує дисципліну витіснення застарілих даних (FIFO Drop), зберігаючи найсвіжіші зрізи телеметрії при вичерпанні ліміту виділеної пам'яті.
4. **Контрольований дренаж черги (Rate-Limited Flusher):**
   * Після відновлення зовнішнього інтернет-з'єднання шлюз відновлює стрімінг оперативних даних, а накопичений історичний масив викачує фоновими пачками з обмеженням швидкості (*Rate Limiting*), щоб не створити лавиноподібне перевантаження радіоканалу та не заблокувати свіжу телеметрію.

### Синхронізація та інваріанти пам'яті

Щоб уникнути стану гонитви (*Race Conditions*) та витоків пам'яті при роботі на мікроконтролерах із обмеженими ресурсами, архітектура спирається на такі правила:
* **Статичне виділення пам'яті під буфер:** У версії на C розмір буфера фіксується під час компіляції (`BUFFER_CAPACITY = 512`), що повністю виключає фрагментацію динамічної купи (Heap Fragmentation) та аварійне завершення через збій `malloc()`.
* **Ізоляція за допомогою м'ютексів:** Усі операції додавання (`push`) та вилучення (`pop`) елементів із черги захищені м'ютексом. Сповіщення потоку-передавача про появу нових даних відбувається через умовну змінну (`pthread_cond_t` у C, `std::condition_variable` у C++).
* **Монотонні ідентифікатори послідовності (Sequence Numbers):** Кожне згенероване повідомлення отримує лічильник `sequence_id`, який не скидається при обриві мережі. Це дозволяє серверу на стороні бекенда точно виявляти факт втрати пакетів у разі переповнення буфера.

Нижче наведено повні реалізації мовами C, C++20 та Python.

### Реалізація на C та C++20

:::tabs
@tab C
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>
#include <pthread.h>
#include <unistd.h>

#define BUFFER_CAPACITY 512
#define TOPIC_MAX_LEN   128
#define PAYLOAD_MAX_LEN 256
#define PRESSURE_ALARM_THRESHOLD 10.0f

/* Структура одного повідомлення телеметрії */
typedef struct {
    char topic[TOPIC_MAX_LEN];
    char payload[PAYLOAD_MAX_LEN];
    time_t timestamp;
    uint32_t sequence_id;
} telemetry_msg_t;

/* Відмовостійкий кільцевий буфер Store-and-Forward */
typedef struct {
    telemetry_msg_t items[BUFFER_CAPACITY];
    size_t head;
    size_t tail;
    size_t count;
    uint32_t dropped_count;
    pthread_mutex_t lock;
    pthread_cond_t not_empty;
} store_forward_queue_t;

static store_forward_queue_t g_queue;
static bool g_wan_connected = false;
static bool g_running = true;
static uint32_t g_seq_counter = 0;

void queue_init(store_forward_queue_t *q) {
    q->head = 0;
    q->tail = 0;
    q->count = 0;
    q->dropped_count = 0;
    pthread_mutex_init(&q->lock, NULL);
    pthread_cond_init(&q->not_empty, NULL);
}

/* Додавання запису: при переповненні витісняється найстаріший (FIFO Drop) */
bool queue_push(store_forward_queue_t *q, const telemetry_msg_t *msg) {
    pthread_mutex_lock(&q->lock);
    if (q->count >= BUFFER_CAPACITY) {
        /* Витіснення найстарішого елемента для збереження свіжих даних */
        q->tail = (q->tail + 1) % BUFFER_CAPACITY;
        q->count--;
        q->dropped_count++;
    }
    q->items[q->head] = *msg;
    q->head = (q->head + 1) % BUFFER_CAPACITY;
    q->count++;
    pthread_cond_signal(&q->not_empty);
    pthread_mutex_unlock(&q->lock);
    return true;
}

bool queue_pop(store_forward_queue_t *q, telemetry_msg_t *out_msg) {
    pthread_mutex_lock(&q->lock);
    if (q->count == 0) {
        pthread_mutex_unlock(&q->lock);
        return false;
    }
    *out_msg = q->items[q->tail];
    q->tail = (q->tail + 1) % BUFFER_CAPACITY;
    q->count--;
    pthread_mutex_unlock(&q->lock);
    return true;
}

/* Емуляція польового опитування Modbus RTU */
void poll_modbus_pressure(void) {
    /* Симуляція отримання двох 16-бітних регістрів (Float32: 0x41200000 = 10.0f) */
    static float simulated_pressure = 8.5f;
    simulated_pressure += ((rand() % 100) - 45) * 0.05f;

    printf("[MODBUS] Опитано вузол #1: тиск = %.2f bar\n", simulated_pressure);

    /* Локальне правило автономії: пряма реакція на аварію */
    if (simulated_pressure > PRESSURE_ALARM_THRESHOLD) {
        printf("[AUTONOMY ALERT] Тиск %.2f > %.1f bar! "
               "Локальна дія: запис Coil 0x0010 = ON (Аварійне скидання)\n",
               simulated_pressure, PRESSURE_ALARM_THRESHOLD);
    }

    /* Формування MQTT-повідомлення */
    telemetry_msg_t msg;
    msg.timestamp = time(NULL);
    msg.sequence_id = ++g_seq_counter;
    snprintf(msg.topic, sizeof(msg.topic), "plant/unit1/telemetry/pressure");
    snprintf(msg.payload, sizeof(msg.payload),
             "{\"dev\":\"boiler_1\",\"val\":%.2f,\"unit\":\"bar\",\"ts\":%ld,\"seq\":%u}",
             simulated_pressure, msg.timestamp, msg.sequence_id);

    queue_push(&g_queue, &msg);
}

/* Емуляція прийому пакетів від BLE-термометра */
void receive_ble_temperature(void) {
    static float simulated_temp = 42.0f;
    simulated_temp += ((rand() % 100) - 50) * 0.02f;

    telemetry_msg_t msg;
    msg.timestamp = time(NULL);
    msg.sequence_id = ++g_seq_counter;
    snprintf(msg.topic, sizeof(msg.topic), "plant/unit1/telemetry/temperature");
    snprintf(msg.payload, sizeof(msg.payload),
             "{\"dev\":\"ble_sensor_a4\",\"val\":%.2f,\"unit\":\"C\",\"ts\":%ld,\"seq\":%u}",
             simulated_temp, msg.timestamp, msg.sequence_id);

    queue_push(&g_queue, &msg);
}

/* Потік публікації та відкладеного викачування (Store-and-Forward Worker) */
void *mqtt_upstream_worker(void *arg) {
    (void)arg;
    telemetry_msg_t msg;

    while (g_running) {
        if (!g_wan_connected) {
            /* WAN відсутній: накопичуємо в черзі, спимо */
            usleep(200000);
            continue;
        }

        /* WAN активний: викачуємо накопичені повідомлення */
        while (g_wan_connected && queue_pop(&g_queue, &msg)) {
            printf("[MQTT PUB] Успішно відправлено -> %s : %s\n",
                   msg.topic, msg.payload);
            /* Згладжування трафіку (Rate limiting: 20 ms між пакетами) */
            usleep(20000);
        }

        usleep(100000);
    }
    return NULL;
}

int main(void) {
    srand(time(NULL));
    queue_init(&g_queue);

    pthread_t worker_tid;
    pthread_create(&worker_tid, NULL, mqtt_upstream_worker, NULL);

    printf("=== Старт IoT-шлюзу (C-версія) ===\n");

    /* Демонстрація життєвого циклу: Онлайн -> Блекаут -> Відновлення */
    for (int step = 1; step <= 10; step++) {
        printf("\n--- ТАКТ СИСТЕМИ %d ---\n", step);

        /* Моделювання стану каналу WAN: кроки 3..7 — блекаут */
        if (step >= 3 && step <= 7) {
            if (g_wan_connected) {
                printf("[WAN] Зв'язок розірвано! Активовано буфер Store-and-Forward.\n");
                g_wan_connected = false;
            }
        } else {
            if (!g_wan_connected) {
                printf("[WAN] Зв'язок відновлено! Старт дренажу буфера.\n");
                g_wan_connected = true;
            }
        }

        poll_modbus_pressure();
        receive_ble_temperature();

        pthread_mutex_lock(&g_queue.lock);
        printf("[BUFFER STATUS] Елементів у буфері: %zu, Втрачено: %u\n",
               g_queue.count, g_queue.dropped_count);
        pthread_mutex_unlock(&g_queue.lock);

        sleep(1);
    }

    g_running = false;
    pthread_join(worker_tid, NULL);
    pthread_mutex_destroy(&g_queue.lock);
    pthread_cond_destroy(&g_queue.not_empty);
    printf("=== Роботу шлюзу завершено ===\n");
    return 0;
}
```
@tab C++
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <deque>
#include <memory>
#include <mutex>
#include <condition_variable>
#include <chrono>
#include <thread>
#include <optional>
#include <random>
#include <format>

struct TelemetryMessage {
    std::string topic;
    std::string payload;
    std::chrono::system_clock::time_point timestamp;
    uint32_t sequence_id{0};
};

/* Потокобезпечний буфер Store-and-Forward з обмеженням розміру (RAII) */
class StoreForwardBuffer {
public:
    explicit StoreForwardBuffer(size_t max_capacity) : max_capacity_(max_capacity) {}

    void push(TelemetryMessage msg) {
        std::lock_guard<std::mutex> lock(mutex_);
        if (queue_.size() >= max_capacity_) {
            queue_.pop_front(); // FIFO drop: видалення застарілих даних
            dropped_count_++;
        }
        queue_.push_back(std::move(msg));
        cv_.notify_one();
    }

    std::optional<TelemetryMessage> pop() {
        std::lock_guard<std::mutex> lock(mutex_);
        if (queue_.empty()) {
            return std::nullopt;
        }
        auto msg = std::move(queue_.front());
        queue_.pop_front();
        return msg;
    }

    [[nodiscard]] size_t size() const {
        std::lock_guard<std::mutex> lock(mutex_);
        return queue_.size();
    }

    [[nodiscard]] uint32_t dropped() const {
        std::lock_guard<std::mutex> lock(mutex_);
        return dropped_count_;
    }

private:
    const size_t max_capacity_;
    std::deque<TelemetryMessage> queue_;
    uint32_t dropped_count_{0};
    mutable std::mutex mutex_;
    std::condition_variable cv_;
};

/* Клас промислового шлюзу */
class IndustrialGateway {
public:
    IndustrialGateway() : buffer_(512), running_(true), wan_connected_(false) {
        upstream_thread_ = std::thread(&IndustrialGateway::upstreamWorker, this);
    }

    ~IndustrialGateway() {
        running_ = false;
        if (upstream_thread_.joinable()) {
            upstream_thread_.join();
        }
    }

    void setWanConnected(bool state) {
        wan_connected_ = state;
    }

    void pollModbusNode(float raw_pressure) {
        std::cout << std::format("[MODBUS C++] Зчитано тиск: {:.2f} bar\n", raw_pressure);

        // Локальний контур безпеки (Edge Autonomy)
        if (raw_pressure > 10.0f) {
            executeEmergencyShutdown(raw_pressure);
        }

        TelemetryMessage msg{
            .topic = "plant/unit1/telemetry/pressure",
            .payload = std::format(R"({{"dev":"boiler_1","val":{:.2f},"unit":"bar"}})", raw_pressure),
            .timestamp = std::chrono::system_clock::now(),
            .sequence_id = ++seq_counter_
        };
        buffer_.push(std::move(msg));
    }

    void receiveBleBeacon(float temperature) {
        TelemetryMessage msg{
            .topic = "plant/unit1/telemetry/temperature",
            .payload = std::format(R"({{"dev":"ble_sensor_a4","val":{:.2f},"unit":"C"}})", temperature),
            .timestamp = std::chrono::system_clock::now(),
            .sequence_id = ++seq_counter_
        };
        buffer_.push(std::move(msg));
    }

    [[nodiscard]] size_t bufferSize() const { return buffer_.size(); }
    [[nodiscard]] uint32_t droppedCount() const { return buffer_.dropped(); }

private:
    void executeEmergencyShutdown(float pressure) {
        std::cout << std::format("[AUTONOMY ALERT C++] Тиск {:.2f} > 10.0 bar! "
                                 "Локальна дія: Modbus Coil 0x0010 = ON\n", pressure);
    }

    void upstreamWorker() {
        while (running_) {
            if (!wan_connected_) {
                std::this_thread::sleep_for(std::chrono::milliseconds(200));
                continue;
            }

            while (wan_connected_) {
                auto msg = buffer_.pop();
                if (!msg) break;

                std::cout << std::format("[MQTT PUB C++] -> {} : {}\n",
                                         msg->topic, msg->payload);
                std::this_thread::sleep_for(std::chrono::milliseconds(20)); // Rate limit
            }
            std::this_thread::sleep_for(std::chrono::milliseconds(100));
        }
    }

    StoreForwardBuffer buffer_;
    std::atomic<bool> running_{false};
    std::atomic<bool> wan_connected_{false};
    std::atomic<uint32_t> seq_counter_{0};
    std::thread upstream_thread_;
};

int main() {
    std::cout << "=== Старт IoT-шлюзу (C++20 версія) ===\n";
    IndustrialGateway gateway;

    std::mt19937 rng(42);
    std::uniform_real_distribution<float> press_dist(7.5f, 11.5f);
    std::uniform_real_distribution<float> temp_dist(38.0f, 44.0f);

    for (int step = 1; step <= 10; ++step) {
        std::cout << std::format("\n--- ТАКТ СИСТЕМИ {} ---\n", step);

        if (step >= 3 && step <= 7) {
            if (step == 3) std::cout << "[WAN] Обрив з'єднання! Активовано Store-and-Forward.\n";
            gateway.setWanConnected(false);
        } else {
            if (step == 8 || step == 1) std::cout << "[WAN] Зв'язок відновлено!\n";
            gateway.setWanConnected(true);
        }

        gateway.pollModbusNode(press_dist(rng));
        gateway.receiveBleBeacon(temp_dist(rng));

        std::cout << std::format("[BUFFER STATUS] У черзі: {}, Втрачено: {}\n",
                                 gateway.bufferSize(), gateway.droppedCount());

        std::this_thread::sleep_for(std::chrono::seconds(1));
    }

    std::cout << "=== Роботу шлюзу завершено ===\n";
    return 0;
}
```
:::

### Реалізація на Python (Asyncio)

```python
import asyncio
import json
import random
import time
from dataclasses import dataclass
from typing import Optional


@dataclass
class TelemetryRecord:
    topic: str
    payload: dict
    timestamp: float
    sequence_id: int


class StoreForwardBuffer:
    """Асинхронний циклічний буфер із витісненням застарілих даних (FIFO Drop)."""

    def __init__(self, max_capacity: int = 500):
        self._max_capacity = max_capacity
        self._queue: list[TelemetryRecord] = []
        self._dropped_count = 0
        self._lock = asyncio.Lock()

    async def push(self, record: TelemetryRecord) -> None:
        async with self._lock:
            if len(self._queue) >= self._max_capacity:
                self._queue.pop(0)  # Витіснення найстарішого запису
                self._dropped_count += 1
            self._queue.append(record)

    async def pop(self) -> Optional[TelemetryRecord]:
        async with self._lock:
            if not self._queue:
                return None
            return self._queue.pop(0)

    @property
    def size(self) -> int:
        return len(self._queue)

    @property
    def dropped(self) -> int:
        return self._dropped_count


class IndustrialIoTGateway:
    """Програмний міст Modbus/BLE-to-MQTT з локальною автономією."""

    PRESSURE_THRESHOLD = 10.0  # bar

    def __init__(self):
        self.buffer = StoreForwardBuffer(max_capacity=500)
        self.wan_connected = False
        self.running = True
        self._seq = 0

    async def execute_autonomy_rule(self, pressure: float) -> None:
        """Прямий локальний контур керування без участі хмари."""
        print(
            f"[AUTONOMY ALERT Py] Критичний тиск {pressure:.2f} bar! "
            f"Локальна дія: Запис Modbus Coil 0x0010 = ON (Аварійне скидання)"
        )

    async def poll_modbus_loop(self) -> None:
        """Задача регулярного опитування Modbus RTU пристроїв."""
        while self.running:
            raw_pressure = 8.0 + random.uniform(-1.0, 3.5)
            self._seq += 1

            print(f"[MODBUS Py] Зчитано тиск: {raw_pressure:.2f} bar")

            # Локальна автономія
            if raw_pressure > self.PRESSURE_THRESHOLD:
                await self.execute_autonomy_rule(raw_pressure)

            record = TelemetryRecord(
                topic="plant/unit1/telemetry/pressure",
                payload={
                    "dev": "boiler_1",
                    "val": round(raw_pressure, 2),
                    "unit": "bar",
                    "ts": time.time(),
                },
                timestamp=time.time(),
                sequence_id=self._seq,
            )
            await self.buffer.push(record)
            await asyncio.sleep(1.0)

    async def receive_ble_loop(self) -> None:
        """Задача отримання телеметрії від бездротових давачів BLE."""
        while self.running:
            raw_temp = 40.0 + random.uniform(-2.0, 4.0)
            self._seq += 1

            record = TelemetryRecord(
                topic="plant/unit1/telemetry/temperature",
                payload={
                    "dev": "ble_sensor_a4",
                    "val": round(raw_temp, 2),
                    "unit": "C",
                    "ts": time.time(),
                },
                timestamp=time.time(),
                sequence_id=self._seq,
            )
            await self.buffer.push(record)
            await asyncio.sleep(1.5)

    async def upstream_mqtt_flusher(self) -> None:
        """Фоновий процес передачі телеметрії та відкладеного дренажу."""
        while self.running:
            if not self.wan_connected:
                await asyncio.sleep(0.2)
                continue

            # Дренаж накопиченої черги зі згладжуванням швидкості
            while self.wan_connected:
                record = await self.buffer.pop()
                if record is None:
                    break

                # Емуляція відправки по MQTT
                serialized = json.dumps(record.payload)
                print(f"[MQTT PUB Py] -> {record.topic} : {serialized}")
                await asyncio.sleep(0.02)  # Rate-limit 50 msg/sec

            await asyncio.sleep(0.1)


async def main():
    gateway = IndustrialIoTGateway()

    # Запуск фонових воркерів
    tasks = [
        asyncio.create_task(gateway.poll_modbus_loop()),
        asyncio.create_task(gateway.receive_ble_loop()),
        asyncio.create_task(gateway.upstream_mqtt_flusher()),
    ]

    print("=== Старт IoT-шлюзу (Python Asyncio) ===")

    # Моделювання 10 тактів роботи
    for step in range(1, 11):
        print(f"\n--- ТАКТ СИСТЕМИ {step} ---")
        if 3 <= step <= 7:
            if gateway.wan_connected or step == 3:
                print(
                    "[WAN] Обрив інтернет-каналу! Активовано буфер Store-and-Forward."
                )
                gateway.wan_connected = False
        else:
            if not gateway.wan_connected:
                print("[WAN] Зв'язок відновлено! Старт фонового дренажу черги.")
                gateway.wan_connected = True

        print(
            f"[BUFFER STATUS] Записів у черзі: {gateway.buffer.size}, "
            f"Втрачено: {gateway.buffer.dropped}"
        )
        await asyncio.sleep(1.0)

    gateway.running = False
    for t in tasks:
        t.cancel()
    print("=== Роботу шлюзу завершено ===")


if __name__ == "__main__":
    asyncio.run(main())
```

### Граничні випадки, гонки потоків та надійність сховища

1. **Захист від пошкодження даних при раптовому знеструмленні (Torn Writes & Power Cut):**
   Якщо вбудована система скидає повідомлення у звичайний файл за допомогою стандартного `fwrite()`, раптове відключення живлення під час оновлення метаданих файлової системи призведе до пошкодження всього файлу буфера. У промислових шлюзах використовують подвійну блочну буферизацію (Ping-Pong Blocks) із валідацією контрольних сум CRC32 для кожного блоку перед записом заголовка готовності або вбудовані бази даних SQLite у режимі журналювання WAL (*Write-Ahead Logging*).
2. **Уникнення шторму синхронізації (Thundering Herd & Network Storm):**
   Коли після масштабного знеструмлення базової станції 4G сотні шлюзів одночасно виходять в онлайн, вони створюють пікове навантаження на стільникову мережу та хмарний брокер. Застосування алгоритму випадкового відступу (*Jitter Backoff*) та суворого обмеження швидкості спорожнення буфера (*Token Bucket Rate Limiting*) гарантує рівномірне завантаження каналу.
3. **Пріоритет свіжих даних над історією (Fresh vs Historical Data Inversion):**
   Неприпустимо блокувати відправку щойно знятих аварійних показників через те, що шлюз зайнятий послідовним викачуванням 100 000 старих записів триденної давнини. Диспетчер висхідного зв'язку зобов'язаний обслуговувати дві черги: свіжі дані завжди передаються першими у пріоритетному сокеті, тоді як фоновий дренаж використовує залишкову пропускну здатність каналу.
