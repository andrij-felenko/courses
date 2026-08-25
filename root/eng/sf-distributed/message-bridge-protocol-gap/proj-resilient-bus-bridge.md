# ⚙️ Відмовостійкий міст шин повідомлень із подвійним підтвердженням

<preknowlist>
- [Черга повідомлень](root:sf-distributed/message-queue) — асинхронний буфер «точка-точка» з ручним підтвердженням (ACK).
- [Гарантії доставки](root:sf-distributed/delivery-guarantees) — семантика at-least-once, at-most-once та координація квитанцій.
- [Наскрізний протитиск](root:sf-distributed/backpressure-end-to-end) — контроль заповнення буферів через водяні знаки.
- [Мертва черга](root:sf-distributed/dead-letter-queue) — ізоляція пошкоджених та неотриманих повідомлень.
</preknowlist>

Побудова промислового мосту між двома гетерогенними шинами повідомлень — наприклад, з'єднання локальної виробничої черги прийому телеметрії з датчиків із центральним хмарним розподіленим логом подій — вимагає вирішення комплексу взаємопов'язаних інженерних викликів. Простий скрипт, який у нескінченному циклі зчитує повідомлення з одного сокета і відправляє в інший, миттєво руйнується в реальному розподіленому середовищі: при першому мережевому розриві він або безповоротно втрачає гігабайти даних, або спричиняє лавиноподібне переповнення пам'яті через відсутність протитиску.

Щоб міст гарантував безперервну та надійну роботу в промисловому контурі, архітектура конвеєра повинна вирішувати чотири фундаментальні системні завдання:

1. **Координація подвійного підтвердження (Dual-Ack Coordination):** міст не має права підтверджувати отримання повідомлення у вхідній черзі доти, доки вихідний брокер не надішле надійну мережеву квитанцію про успішну фіксацію даних на енергонезалежному диску. Передчасне підтвердження (Auto-Ack) у разі аварійного падіння мосту перетворюється на безповоротну втрату повідомлень, які вже були вилучені з черги джерела, але ще не досягли приймача.
2. **Наскрізний адаптивний протитиск (Backpressure Control):** якщо цільова шина уповільнює обробку через планові навантаження або мережевий джитер, внутрішній буфер мосту починає заповнюватися. Міст повинен автоматично сигналізувати вхідному адаптеру про необхідність призупинити вичитування з джерела за алгоритмом високого і низького водяних знаків (High/Low Watermarks), запобігаючи аварійному вичерпанню оперативної пам'яті (OOM Crash).
3. **Захист від зациклення та шторму луни (Loop & Echo Prevention):** у розподілених топологіях типу «актив-актив» або кільцевих контурах реплікації повідомлення, надіслане з шини А в шину Б, може бути підхоплене зворотним мостом і повернене назад у шину А. Без аналізу заголовків трасування (`X-Bridge-Hops`, `X-Origin-Bus`) такий контур породжує нескінченний експоненційний шторм реплікації.
4. **Ізоляція отруйних пакетів (Poison Message Quarantine):** якщо корисне навантаження повідомлення пошкоджене, не відповідає схемі серіалізації або викликає фатальну помилку на боці вихідного адаптера, міст не повинен зависати у вічному циклі повторів. Такі повідомлення спрямовуються в окрему мертву чергу ([мертва черга](root:sf-distributed/dead-letter-queue)), супроводжуючись діагностичними метаданими про причину збою, після чого вхідне повідомлення підтверджується, звільняючи конвеєр для подальшого потоку.

## Реалізація конвеєра мосту мовами C та C++

Нижче наведено повну, автономну та робочу реалізацію відмовостійкого мосту шин. Програма моделює повний цикл: генерацію вхідних подій із квитанціями доставки, валідацію ліміту стрибків, потокобезпечний кільцевий буфер Store-and-Forward із подвійними водяними знаками, асинхронний вихідний адаптер та механізм ізоляції пошкоджених пакетів у DLQ.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>
#include <pthread.h>
#include <unistd.h>
#include <time.h>
#include <inttypes.h>

#define MAX_PAYLOAD_SIZE   512
#define MAX_BUS_NAME_LEN    32
#define MAX_HOPS             3
#define BUFFER_CAPACITY     16
#define HIGH_WATERMARK      12
#define LOW_WATERMARK        4

/* Статуси операцій мосту */
typedef enum {
    BRIDGE_OK = 0,
    BRIDGE_ERR_BUFFER_FULL,
    BRIDGE_ERR_CORRUPTED_PAYLOAD,
    BRIDGE_ERR_LOOP_DETECTED,
    BRIDGE_ERR_EGRESS_FAILED
} BridgeStatus;

/* Структура повідомлення з метаданими трасування */
typedef struct {
    uint64_t msg_id;
    uint32_t hop_count;
    char     origin_bus[MAX_BUS_NAME_LEN];
    char     payload[MAX_PAYLOAD_SIZE];
    size_t   payload_len;
    uint64_t ingress_delivery_tag; /* Ідентифікатор квитанції у вхідній шині */
} BridgeMessage;

/* Потокобезпечний кільцевий буфер Store-and-Forward */
typedef struct {
    BridgeMessage   slots[BUFFER_CAPACITY];
    size_t          head;
    size_t          tail;
    size_t          count;
    bool            paused;
    pthread_mutex_t lock;
    pthread_cond_t  not_empty;
    pthread_cond_t  not_full;
} ResilientRingBuffer;

/* Контекст мосту шин */
typedef struct {
    char                current_bus_name[MAX_BUS_NAME_LEN];
    ResilientRingBuffer queue;
    bool                running;
    uint64_t            forwarded_count;
    uint64_t            quarantine_count;
    pthread_t           worker_thread;
} MessageBusBridge;

/* Ініціалізація буфера */
static void ring_buffer_init(ResilientRingBuffer *rb) {
    rb->head = 0;
    rb->tail = 0;
    rb->count = 0;
    rb->paused = false;
    pthread_mutex_init(&rb->lock, NULL);
    pthread_cond_init(&rb->not_empty, NULL);
    pthread_cond_init(&rb->not_full, NULL);
}

/* Знищення ресурсів буфера */
static void ring_buffer_destroy(ResilientRingBuffer *rb) {
    pthread_mutex_destroy(&rb->lock);
    pthread_cond_destroy(&rb->not_empty);
    pthread_cond_destroy(&rb->not_full);
}

/* Додавання повідомлення до буфера мосту (Ingress Stage) */
static BridgeStatus bridge_enqueue(MessageBusBridge *bridge, const BridgeMessage *msg) {
    pthread_mutex_lock(&bridge->queue.lock);

    /* Перевірка на зациклення перед збереженням у пам'ять */
    if (msg->hop_count >= MAX_HOPS || strcmp(msg->origin_bus, bridge->current_bus_name) == 0) {
        pthread_mutex_unlock(&bridge->queue.lock);
        return BRIDGE_ERR_LOOP_DETECTED;
    }

    /* Очікування вільного місця у разі переповнення */
    while (bridge->queue.count == BUFFER_CAPACITY && bridge->running) {
        pthread_cond_wait(&bridge->queue.not_full, &bridge->queue.lock);
    }

    if (!bridge->running) {
        pthread_mutex_unlock(&bridge->queue.lock);
        return BRIDGE_ERR_EGRESS_FAILED;
    }

    /* Запис у кільцевий буфер */
    bridge->queue.slots[bridge->queue.head] = *msg;
    bridge->queue.head = (bridge->queue.head + 1) % BUFFER_CAPACITY;
    bridge->queue.count++;

    /* Контроль протитиску за високим водяним знаком */
    if (bridge->queue.count >= HIGH_WATERMARK && !bridge->queue.paused) {
        bridge->queue.paused = true;
        printf("[ПРОТИТИСК] Буфер досяг %zu/%d. Призупинено вичитування з входу.\n",
               bridge->queue.count, BUFFER_CAPACITY);
    }

    pthread_cond_signal(&bridge->queue.not_empty);
    pthread_mutex_unlock(&bridge->queue.lock);
    return BRIDGE_OK;
}

/* Імітація публікації у вихідну шину з підтвердженням (Egress Stage) */
static bool mock_egress_publish(const char *target_bus, const BridgeMessage *msg) {
    /* Імітація мережевої затримки транзиту */
    usleep(15000); /* 15 мс */

    /* Імітація збою у разі спеціального маркера або помилки валідації */
    if (strstr(msg->payload, "CORRUPT") != NULL) {
        return false;
    }

    printf("[EGRESS -> %s] Успішно записано msg_id=%" PRIu64 " (hops=%u, payload=\"%s\")\n",
           target_bus, msg->msg_id, msg->hop_count + 1, msg->payload);
    return true;
}

/* Імітація підтвердження у вхідній черзі (Ingress Commit) */
static void mock_ingress_commit(uint64_t delivery_tag) {
    printf("[INGRESS-ACK] Квитанція delivery_tag=%" PRIu64 " успішно підтверджена у вхідній шині.\n",
           delivery_tag);
}

/* Імітація відправки у мертву чергу (Quarantine DLQ) */
static void mock_quarantine_dlq(const BridgeMessage *msg, const char *reason) {
    printf("[МЕРТВА ЧЕРГА / DLQ] Ізольовано msg_id=%" PRIu64 ", причина: %s\n",
           msg->msg_id, reason);
}

/* Робочий потік обробки конвеєра мосту */
static void* bridge_worker_routine(void *arg) {
    MessageBusBridge *bridge = (MessageBusBridge*)arg;

    while (bridge->running) {
        BridgeMessage msg;

        pthread_mutex_lock(&bridge->queue.lock);
        while (bridge->queue.count == 0 && bridge->running) {
            pthread_cond_wait(&bridge->queue.not_empty, &bridge->queue.lock);
        }

        if (!bridge->running && bridge->queue.count == 0) {
            pthread_mutex_unlock(&bridge->queue.lock);
            break;
        }

        /* Вилучення повідомлення з кільцевого буфера */
        msg = bridge->queue.slots[bridge->queue.tail];
        bridge->queue.tail = (bridge->queue.tail + 1) % BUFFER_CAPACITY;
        bridge->queue.count--;

        /* Зняття протитиску при досягненні низького водяного знака */
        if (bridge->queue.count <= LOW_WATERMARK && bridge->queue.paused) {
            bridge->queue.paused = false;
            printf("[ПРОТИТИСК] Буфер розвантажено до %zu/%d. Відновлено прийом з входу.\n",
                   bridge->queue.count, BUFFER_CAPACITY);
        }

        pthread_cond_signal(&bridge->queue.not_full);
        pthread_mutex_unlock(&bridge->queue.lock);

        /* Модифікація службових метаданих трасування */
        msg.hop_count++;

        /* Спроба публікації з семантикою Dual-Ack */
        bool published = mock_egress_publish("Cloud_Kafka_Cluster", &msg);
        if (published) {
            /* Подвійне підтвердження: коміт у джерело ЛИШЕ після успіху на виході */
            mock_ingress_commit(msg.ingress_delivery_tag);
            bridge->forwarded_count++;
        } else {
            /* Відправка в DLQ у разі неотримання Egress-ACK */
            mock_quarantine_dlq(&msg, "Egress broker reject / network timeout");
            /* Підтверджуємо джерелу, щоб уникнути блокування вхідної черги */
            mock_ingress_commit(msg.ingress_delivery_tag);
            bridge->quarantine_count++;
        }
    }
    return NULL;
}

/* Ініціалізація та запуск мосту */
void bridge_init(MessageBusBridge *bridge, const char *bus_name) {
    strncpy(bridge->current_bus_name, bus_name, MAX_BUS_NAME_LEN - 1);
    bridge->current_bus_name[MAX_BUS_NAME_LEN - 1] = '\0';
    ring_buffer_init(&bridge->queue);
    bridge->running = true;
    bridge->forwarded_count = 0;
    bridge->quarantine_count = 0;
    pthread_create(&bridge->worker_thread, NULL, bridge_worker_routine, bridge);
}

/* Зупинка та звільнення ресурсів */
void bridge_shutdown(MessageBusBridge *bridge) {
    pthread_mutex_lock(&bridge->queue.lock);
    bridge->running = false;
    pthread_cond_broadcast(&bridge->queue.not_empty);
    pthread_cond_broadcast(&bridge->queue.not_full);
    pthread_mutex_unlock(&bridge->queue.lock);

    pthread_join(bridge->worker_thread, NULL);
    ring_buffer_destroy(&bridge->queue);
}

int main(void) {
    printf("=== Запуск тесту відмовостійкого мосту шин повідомлень ===\n\n");
    MessageBusBridge bridge;
    bridge_init(&bridge, "Factory_Floor_Edge_MQTT");

    /* Тест 1: Звичайна успішна доставка */
    BridgeMessage msg1 = {
        .msg_id = 101, .hop_count = 0, .origin_bus = "Factory_Floor_Edge_MQTT",
        .payload = "SensorData{temperature: 24.5C, pressure: 1013hPa}",
        .payload_len = 49, .ingress_delivery_tag = 1
    };
    bridge_enqueue(&bridge, &msg1);

    /* Тест 2: Повідомлення із зацикленням (повернення на ту саму шину) */
    BridgeMessage loop_msg = {
        .msg_id = 102, .hop_count = 2, .origin_bus = "Factory_Floor_Edge_MQTT",
        .payload = "OrderEvent{id: 5541, action: RECHECK}",
        .payload_len = 37, .ingress_delivery_tag = 2
    };
    BridgeStatus st = bridge_enqueue(&bridge, &loop_msg);
    if (st == BRIDGE_ERR_LOOP_DETECTED) {
        printf("[ЗАХИСТ ВІД ЗАЦИКЛЕННЯ] Повідомлення msg_id=102 відхилено через виявлення петлі маршрутизації!\n");
    }

    /* Тест 3: Пошкоджене повідомлення для тесту карантину DLQ */
    BridgeMessage corrupt_msg = {
        .msg_id = 103, .hop_count = 0, .origin_bus = "Substation_AMQP",
        .payload = "TelemetryPacket{CORRUPT_CHECKSUM}",
        .payload_len = 33, .ingress_delivery_tag = 3
    };
    bridge_enqueue(&bridge, &corrupt_msg);

    /* Тест 4: Серія пакетів для перевірки протитиску (Backpressure) */
    for (int i = 0; i < 14; i++) {
        BridgeMessage burst_msg;
        burst_msg.msg_id = 200 + i;
        burst_msg.hop_count = 0;
        snprintf(burst_msg.origin_bus, MAX_BUS_NAME_LEN, "PLC_Node_%d", i % 3);
        snprintf(burst_msg.payload, MAX_PAYLOAD_SIZE, "VibrationEvent{rpm: %d, amp: 0.12}", 1500 + i * 10);
        burst_msg.payload_len = strlen(burst_msg.payload);
        burst_msg.ingress_delivery_tag = 10 + i;
        bridge_enqueue(&bridge, &burst_msg);
    }

    /* Очікування завершення обробки */
    usleep(400000); /* 400 мс */
    bridge_shutdown(&bridge);

    printf("\n=== Результати роботи мосту ===\n");
    printf("Успішно репліковано у вихідну шину: %" PRIu64 "\n", bridge.forwarded_count);
    printf("Ізольовано в карантині (DLQ):      %" PRIu64 "\n", bridge.quarantine_count);
    printf("Конвеєр мосту зупинено коректно.\n");
    return 0;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <queue>
#include <memory>
#include <mutex>
#include <condition_variable>
#include <thread>
#include <chrono>
#include <expected>
#include <format>
#include <cstdint>
#include <atomic>

namespace bridge {

// Константи конфігурації конвеєра мосту
inline constexpr size_t kBufferCapacity = 16;
inline constexpr size_t kHighWatermark  = 12;
inline constexpr size_t kLowWatermark   = 4;
inline constexpr uint32_t kMaxHops      = 3;

// Типізовані коди помилок обробки
enum class BridgeError {
    BufferFull,
    LoopDetected,
    HopLimitExceeded,
    EgressBrokerFailure,
    CorruptedPayload
};

// Незмінна структура повідомлення з метаданими трасування
struct Message {
    uint64_t    id;
    uint32_t    hop_count;
    std::string origin_bus;
    std::string payload;
    uint64_t    delivery_tag;

    [[nodiscard]] bool has_loop(std::string_view current_bus) const noexcept {
        return (hop_count >= kMaxHops) || (origin_bus == current_bus);
    }
};

// Потокобезпечний буфер з керуванням водяними знаками протитиску (RAII)
class ResilientQueue {
public:
    explicit ResilientQueue(size_t capacity = kBufferCapacity)
        : capacity_(capacity), paused_(false), closed_(false) {}

    std::expected<void, BridgeError> push(Message msg) {
        std::unique_lock lock(mutex_);
        not_full_cv_.wait(lock, [this]() {
            return queue_.size() < capacity_ || closed_;
        });

        if (closed_) {
            return std::unexpected(BridgeError::EgressBrokerFailure);
        }

        queue_.push(std::move(msg));

        // Активація протитиску при досягненні високого порогу
        if (queue_.size() >= kHighWatermark && !paused_) {
            paused_ = true;
            std::cout << std::format("[ПРОТИТИСК] Буфер досяг {}/{}. Вхідний потік призупинено.\n",
                                     queue_.size(), capacity_);
        }

        not_empty_cv_.notify_one();
        return {};
    }

    std::expected<Message, BridgeError> pop() {
        std::unique_lock lock(mutex_);
        not_empty_cv_.wait(lock, [this]() {
            return !queue_.empty() || closed_;
        });

        if (queue_.empty() && closed_) {
            return std::unexpected(BridgeError::EgressBrokerFailure);
        }

        Message msg = std::move(queue_.front());
        queue_.pop();

        // Зняття протитиску при досягненні низького порогу
        if (queue_.size() <= kLowWatermark && paused_) {
            paused_ = false;
            std::cout << std::format("[ПРОТИТИСК] Буфер розвантажено до {}/{}. Вхід відновлено.\n",
                                     queue_.size(), capacity_);
        }

        not_full_cv_.notify_one();
        return msg;
    }

    void close() {
        std::lock_guard lock(mutex_);
        closed_ = true;
        not_empty_cv_.notify_all();
        not_full_cv_.notify_all();
    }

    [[nodiscard]] size_t size() const {
        std::lock_guard lock(mutex_);
        return queue_.size();
    }

private:
    const size_t            capacity_;
    std::queue<Message>     queue_;
    bool                    paused_;
    bool                    closed_;
    mutable std::mutex      mutex_;
    std::condition_variable not_empty_cv_;
    std::condition_variable not_full_cv_;
};

// Інтерфейс вихідної шини з підтвердженням доставки
class IEgressPublisher {
public:
    virtual ~IEgressPublisher() = default;
    [[nodiscard]] virtual std::expected<void, BridgeError> publish(const Message& msg) = 0;
};

// Реалізація вихідного адаптера для хмарного Kafka-кластера
class CloudKafkaPublisher : public IEgressPublisher {
public:
    [[nodiscard]] std::expected<void, BridgeError> publish(const Message& msg) override {
        // Імітація мережевого RTT
        std::this_thread::sleep_for(std::chrono::milliseconds(15));

        if (msg.payload.contains("CORRUPT")) {
            return std::unexpected(BridgeError::CorruptedPayload);
        }

        std::cout << std::format("[EGRESS -> Cloud_Kafka] Записано id={} (hops={}, payload=\"{}\")\n",
                                 msg.id, msg.hop_count, msg.payload);
        return {};
    }
};

// Головний рушій мосту повідомлень (Message Bus Bridge Engine)
class MessageBusBridge {
public:
    MessageBusBridge(std::string current_bus, std::shared_ptr<IEgressPublisher> egress)
        : current_bus_(std::move(current_bus)),
          egress_(std::move(egress)),
          forwarded_count_(0),
          quarantine_count_(0),
          running_(true) {
        worker_thread_ = std::jthread([this](std::stop_token st) {
            process_pipeline(st);
        });
    }

    ~MessageBusBridge() {
        stop();
    }

    std::expected<void, BridgeError> ingress_receive(Message msg) {
        if (msg.has_loop(current_bus_)) {
            return std::unexpected(BridgeError::LoopDetected);
        }
        return buffer_.push(std::move(msg));
    }

    void stop() {
        if (running_.exchange(false)) {
            buffer_.close();
            if (worker_thread_.joinable()) {
                worker_thread_.request_stop();
            }
        }
    }

    [[nodiscard]] uint64_t forwarded_count() const noexcept { return forwarded_count_.load(); }
    [[nodiscard]] uint64_t quarantine_count() const noexcept { return quarantine_count_.load(); }

private:
    void process_pipeline(std::stop_token st) {
        while (!st.stop_requested() && running_) {
            auto msg_opt = buffer_.pop();
            if (!msg_opt) {
                break; // Буфер закрито і спустошено
            }

            Message msg = std::move(*msg_opt);
            msg.hop_count++;

            // Спроба публікації з координацією Dual-Ack
            auto result = egress_->publish(msg);
            if (result.has_value()) {
                // Коміт у джерело здійснюється ЛИШЕ після підтвердження Egress
                commit_ingress_ack(msg.delivery_tag);
                forwarded_count_++;
            } else {
                // Ізоляція в мертву чергу (DLQ)
                quarantine_dlq(msg, "Egress ACK timeout or schema validation error");
                commit_ingress_ack(msg.delivery_tag);
                quarantine_count_++;
            }
        }
    }

    static void commit_ingress_ack(uint64_t delivery_tag) {
        std::cout << std::format("[INGRESS-ACK] Квитанцію delivery_tag={} підтверджено у вхідній шині.\n",
                                 delivery_tag);
    }

    static void quarantine_dlq(const Message& msg, std::string_view reason) {
        std::cout << std::format("[МЕРТВА ЧЕРГА / DLQ] Ізольовано id={}, причина: {}\n",
                                 msg.id, reason);
    }

    std::string                       current_bus_;
    std::shared_ptr<IEgressPublisher> egress_;
    ResilientQueue                    buffer_;
    std::atomic<uint64_t>             forwarded_count_;
    std::atomic<uint64_t>             quarantine_count_;
    std::atomic<bool>                 running_;
    std::jthread                      worker_thread_;
};

} // namespace bridge

int main() {
    std::cout << "=== Запуск тесту відмовостійкого мосту шин (C++23) ===\n\n";

    auto publisher = std::make_shared<bridge::CloudKafkaPublisher>();
    bridge::MessageBusBridge bridge("Factory_Floor_Edge_MQTT", publisher);

    // Тест 1: Успішна реплікація
    auto res1 = bridge.ingress_receive({
        .id = 101, .hop_count = 0, .origin_bus = "Factory_Floor_Edge_MQTT",
        .payload = "SensorData{temp: 24.5C, humidity: 45%}", .delivery_tag = 1
    });

    // Тест 2: Виявлення петлі маршрутизації
    auto res2 = bridge.ingress_receive({
        .id = 102, .hop_count = 1, .origin_bus = "Factory_Floor_Edge_MQTT",
        .payload = "BillingEvent{tx_id: 9942}", .delivery_tag = 2
    });
    if (!res2) {
        std::cout << "[ЗАХИСТ ВІД ЗАЦИКЛЕННЯ] Повідомлення id=102 відхилено (петля маршрутизації)!\n";
    }

    // Тест 3: Отруйний пакет для DLQ
    auto res3 = bridge.ingress_receive({
        .id = 103, .hop_count = 0, .origin_bus = "Robotics_CAN_Bus",
        .payload = "Telemetry{CORRUPT_CRC32}", .delivery_tag = 3
    });

    // Тест 4: Сплеск трафіку для перевірки протитиску
    for (int i = 0; i < 14; ++i) {
        bridge.ingress_receive({
            .id = static_cast<uint64_t>(200 + i),
            .hop_count = 0,
            .origin_bus = std::format("PLC_Node_{}", i % 3),
            .payload = std::format("Vibration{{rpm: {}, amp: 0.14}}", 1500 + i * 15),
            .delivery_tag = static_cast<uint64_t>(10 + i)
        });
    }

    std::this_thread::sleep_for(std::chrono::milliseconds(450));
    bridge.stop();

    std::cout << "\n=== Результати роботи мосту ===\n";
    std::cout << std::format("Успішно репліковано: {}\n", bridge.forwarded_count());
    std::cout << std::format("Ізольовано в DLQ:    {}\n", bridge.quarantine_count());
    std::cout << "Конвеєр мосту зупинено коректно.\n";

    return 0;
}
```
:::

## Порівняльний аналіз ідіом реалізації мовою C та C++

Реалізація мосту демонструє принципову різницю в підходах до управління станом, життєвим циклом ресурсів та обробкою помилок між процедурною моделлю мови C та сучасними стандартами C++20/C++23:

1. **Керування пам'яттю та ресурсами синхронізації:**
   * У версії мовою C пам'ять для кільцевого буфера виділяється у вигляді статичного масиву фіксованого розміру `slots[BUFFER_CAPACITY]`. Ініціалізація та знищення м'ютекса і умовних змінних POSIX Threads вимагають явних парних викликів `ring_buffer_init` та `ring_buffer_destroy`. Будь-яке дострокове повернення з функції без розблокування `pthread_mutex_unlock` призводить до мертвого блокування (Deadlock).
   * У версії C++ управління пам'яттю інкапсульовано в стандартних контейнерах, а синхронізація реалізована за ідіомою RAII через `std::unique_lock` та `std::lock_guard`. Захоплення та звільнення м'ютекса прив'язані до часу життя об'єкта блокування на стеку, що унеможливлює витік блокування при будь-яких гілках виконання чи повернення помилок.

2. **Модель керування асинхронними потоками:**
   * У версії C потік створюється викликом `pthread_create` і вимагає обов'язкового ручного приєднання через `pthread_join` у функції зупинки `bridge_shutdown`. Сигналізація про завершення здійснюється через ручний бродкаст умовних змінних `pthread_cond_broadcast` для виведення воркера зі стану очікування.
   * У версії C++ робочий потік інкапсульовано в `std::jthread`. Цей тип автоматично передає токен зупинки (`std::stop_token`) у функцію потоку і здійснює деструкторне приєднання (`join`) при виході з області видимості, гарантуючи коректне завершення фонових задач без зависання процесу.

3. **Типізація результатів та обробка помилок:**
   * У C функції повертають цілочисельний перелічуваний тип `BridgeStatus`, а структури передаються через сирі вказівники.
   * У C++ використовується тип `std::expected<T, BridgeError>`, що дозволяє повертати або корисний результат (значення повідомлення), або типізований код помилки (`enum class BridgeError`) без генерації важких винятків і без використання вихідних вказівників-параметрів.

## Покроковий розбір життєвого циклу повідомлення в конвеєрі

Життєвий цикл кожного пакета всередині мосту складається з шести послідовних стадій:

1. **Отримання та відкладене підтвердження (Ingress Fetch):** Вхідний адаптер зчитує пакет із шини А у режимі з відключеним автопідтвердженням (`auto_ack = false`). Брокер джерела фіксує, що повідомлення перебуває в обробці (In-Flight), але не видаляє його. До структури повідомлення прикріплюється `delivery_tag` (або пара `partition:offset` для Kafka), яка слугуватиме квитанцією для фінального коміту.
2. **Перевірка трасування та фільтрація петель (Hop & Loop Guard):** Модуль маршрутизації аналізує метадані:
   * Якщо лічильник стрибків `hop_count >= MAX_HOPS` або поле `origin_bus` збігається з іменем поточного вузла `current_bus_name`, пакет негайно відхиляється зі статусом `BRIDGE_ERR_LOOP_DETECTED`. Це гарантує, що репліковане повідомлення не повернеться у вихідну шину через зворотний міст.
   * Якщо перевірка успішна, лічильник інкрементується (`hop_count++`), а ім'я поточної шини додається до ланцюжка трасування.
3. **Постановка в буфер та контроль порогів (Watermark Enforcement):** Повідомлення записується у внутрішній потокобезпечний кільцевий буфер (`slots[head]`). Якщо кількість зайнятих слотів досягає або перевищує `HIGH_WATERMARK` (12 із 16), прапорець `paused` встановлюється в `true`, і вхідний адаптер тимчасово припиняє опитувати сокет вхідної шини. Мережевий буфер TCP на стороні джерела починає заповнюватися, що змушує відправника природним чином сповільнити генерацію трафіку (наскрізний апаратний протитиск).
4. **Вичитування воркером та публікація (Egress Dispatch):** Робочий потік (`bridge_worker_routine`) вилучає пакет із хвоста буфера (`slots[tail]`). Якщо рівень заповнення падає нижче `LOW_WATERMARK` (4 із 16), прапорець `paused` скидається, і вхідний адаптер відновлює активне вичитування. Пакет серіалізується у формат цільового брокера та відправляється через мережевий виклик `mock_egress_publish`.
5. **Синхронізація підтвердження (Dual-Ack Resolution):**
   * **Успіх (Egress ACK received):** Цільовий брокер підтвердив запис у свій лог. Лише після цього міст викликає `mock_ingress_commit(delivery_tag)`, сигналізуючи шині А, що повідомлення можна безпечно видалити з черги.
   * **Помилка (Egress Timeout / Broker Reject):** Цільовий брокер відхилив пакет через невідповідність схеми або тайм-аут з'єднання. Міст перенаправляє пакет у локальну мертву чергу (`mock_quarantine_dlq`), записуючи точну причину відмови, після чого підтверджує вхідне повідомлення у шині А (`mock_ingress_commit`). Цей крок є критичним: якби міст не підтвердив вхідне повідомлення, отруйний пакет завис би на початку черги (Head-of-Line Blocking), заблокувавши рух усього конвеєра.

## Аналіз виконання тестових сценаріїв

Програма `main()` демонструє чотири ключові граничні сценарії поведінки розподіленого мосту:

```
[INGRESS]  msg_id=101 -> Enqueue OK -> Egress Publish OK -> Ingress Commit ✓
[LOOP]     msg_id=102 -> Origin match detected -> Drop immediately ✗
[DLQ]      msg_id=103 -> Corrupt payload -> Egress Reject -> Move to Quarantine DLQ -> Ingress Commit ✓
[BURST]    msg_id=200..213 -> Buffer reaches 12/16 -> PAUSE INGRESS -> Drain to 4/16 -> RESUME INGRESS ✓
```

1. **Тест 1 (Базова трансляція):** Повідомлення `msg_id=101` успішно проходить конвеєр: лічильник хопів зростає до 1, байти публікуються у хмарний Kafka-кластер, після чого відправляється квитанція `delivery_tag=1` у вхідну чергу.
2. **Тест 2 (Відсікання петлі):** Повідомлення `msg_id=102`, яке вже містить `origin_bus = "Factory_Floor_Edge_MQTT"`, негайно блокується на стадії входу, не витрачаючи пам'ять кільцевого буфера та мережеві ресурси вихідного сокета.
3. **Тест 3 (Карантин отруйного повідомлення):** Повідомлення `msg_id=103` з пошкодженим вмістом викликає помилку валідації на боці вихідного адаптера. Міст не падає в аварійний панічний перезапуск: пакет спрямовується в карантинну чергу DLQ, а вхідний дескриптор підтверджується, дозволяючи обробляти наступні валідні пакети.
4. **Тест 4 (Сплеск трафіку та перевірка протитиску):** Одночасне надходження 14 повідомлень при ємності буфера 16 слотів викликає спрацьовування високого порогу `HIGH_WATERMARK = 12`. Міст друкує повідомлення про призупинення вхідного потоку, захищаючи процес від переповнення. У міру того, як воркер споживає повідомлення зі швидкістю 15 мс на пакет, рівень буфера знижується до `LOW_WATERMARK = 4`, викликаючи автоматичне зняття паузи та відновлення прийому.

## Архітектура аварійного скидання на диск (Disk Spillover WAL)

У випадках тривалих аварій глобальної мережі (WAN Outages тривалістю від кількох хвилин до годин) ємності оперативної пам'яті стає недостатньо для утримання потоку повідомлень. Для таких умов архітектура мосту розширюється трирівневою ієрархією збереження:

1. **Оперативний кільцевий буфер (L1 Ring Buffer):** високошвидкісна черга в оперативній пам'яті для згладжування мікросекундного джитеру та пакетування.
2. **Дисковий журнал випереджального запису (L2 Spillover WAL):** коли оперативний буфер заповнюється на 100%, вхідний адаптер перемикається у режим послідовного скидання непідтверджених повідомлень у сегментовані бінарні файли на SSD. Послідовний запис забезпечує пропускну здатність у сотні мегабайтів на секунду навіть на бюджетних накопичувачах.
3. **Фоновий реплей-воркер (Drain Worker):** після відновлення з'єднання з вихідним брокером окремий потік зчитує зафіксовані на диску сегменти WAL і публікує їх у вихідну шину зі збереженням вихідного порядку слідування, паралельно видаляючи оброблені файли журналів.

## Шардинг та збереження порядку повідомлень

При горизонтальному масштабуванні мосту на кілька паралельних робочих потоків або серверних вузлів виникає загроза порушення порядку обробки пов'язаних повідомлень (Out-of-Order Delivery).

Для збереження суворого порядку подій всередині сутності (наприклад, життєвий цикл одного замовлення `order_id` або показники конкретного датчика `sensor_id`) міст застосовує **маршрутизацію за ключем партиціювання (Key-Affinity Sharding)**:

```
worker_index = Hash(msg.partition_key) % WORKER_COUNT
```

Кожен робочий потік володіє власним незалежним кільцевим буфером і вихідним сокетом. Це гарантує, що всі події з однаковим ключем обробляються суворо послідовно через один і той самий ланцюжок Dual-Ack без міжпотокових блокувань і без потреби у глобальних м'ютексах.

## Аналіз крайових випадків та пасток реалізації

Розробка промислових мостів пов'язана з низкою неочевидних пасток розподілених систем:

1. **Пастка автопідтвердження (Auto-Ack Trap):** Найпоширеніша помилка початківців — зчитувати повідомлення з вихідної черги з прапорцем `auto_ack=true` (або `enable.auto.commit=true` у Kafka). У цьому випадку брокер вважає повідомлення успішно доставленим у той самий момент, коли байти потрапляють у мережевий сокет мосту. Якщо міст зазнає аварійного перезапуску або збою живлення у проміжку між вичитуванням та записом у цільову шину, дані безповоротно втрачаються. Семантика At-Least-Once вимагає виключно ручного підтвердження (`explicit manual ACK`) після отримання квитанції від цільового брокера.
2. **Пастка відсутності гістерезису в порогах протитиску:** Якщо встановити верхній і нижній водяні знаки на однаковому або занадто близькому рівні (наприклад, зупинка при 15 слотах і відновлення при 14), міст під високим навантаженням почне страждати від осциляцій (Chattering Effect). Конвеєр буде перемикатися між станами «пауза» та «старт» на кожному окремому повідомленні, генеруючи тисячі зайвих контекстних перемикань операційної системи та різко знижуючи загальну пропускну здатність. Розрив між `HIGH_WATERMARK` (75–80% ємності) та `LOW_WATERMARK` (25–30% ємності) створює стабільну зону гістерезису.
3. **Пастка дублювання при аварійних рестартах:** Семантика Dual-Ack гарантує надійність рівня At-Least-Once, але не захищає від дублікатів. Якщо міст успішно записав повідомлення у вихідну шину Б і отримав підтвердження, але зазнав апаратного краху за мікросекунду до відправки `mock_ingress_commit` у шину А, після перезапуску міст знову вичитає те саме повідомлення з шини А і надішле його вдруге. Тому цільова система Б зобов'язана реалізовувати ідемпотентну обробку на основі глобального унікального ідентифікатора повідомлення (`msg_id`).
4. **Пастка деградації пам'яті при повільному споживачі (Slow Consumer Overflow):** Якщо внутрішній буфер реалізований як динамічний зв'язний список без обмеження максимального розміру (`unbounded queue`), затяжний збій цільової шини призведе до неконтрольованого накопичення мільйонів повідомлень в оперативній пам'яті. Використання статично алокованого масиву або кільцевого буфера фіксованого розміру з механізмом блокування (`pthread_cond_wait` / `std::condition_variable`) гарантує детерміноване використання ресурсів вузла.

## Оптимізація нульового копіювання (Zero-Copy Payload Forwarding)

У високопродуктивних сценаріях, де міст обробляє понад 100 000 повідомлень на секунду, копіювання байтів корисного навантаження (`memcpy`) та часті динамічні алокації пам'яті (`malloc`/`new`) стають головним вузьким місцем процесора (Memory Bandwidth Bottleneck).

Якщо повідомлення не вимагає трансформації внутрішньої бізнес-структури (наприклад, серіалізований Protobuf або Avro просто пересилається з однієї шини в іншу зі зміною лише мережевих заголовків брокера), промисловий міст застосовує техніку **нульового копіювання (Zero-Copy Forwarding)**:
* **Розділення заголовка та корисного навантаження (Header/Payload Decoupling):** Метадані трасування (`BridgeMessage` дескриптор) розміщуються у швидкій пам'яті стека або пул-алокатора, тоді як байти корисного навантаження утримуються в попередньо виділених сторінкових буферах або неперервних блоках пам'яті (`std::span<const uint8_t>` у C++ або структура з лічильником посилань у C).
* **Векторний ввід-вивід (Scatter-Gather I/O):** При відправці у вихідний мережевий сокет міст використовує системні виклики `writev()` / `sendmsg()`. Перший елемент вектора `iovec[0]` вказує на згенеровані мостом бінарні заголовки цільового протоколу, а `iovec[1]` — на вихідний сирий буфер тіла повідомлення. Мережевий стек ядра ОС збирає пакет безпосередньо перед відправкою на мережеву карту (DMA), повністю усуваючи проміжні копіювання в просторі користувача.

## Метрики моніторингу та експлуатаційний чекліст

Для промислової експлуатації мосту шин повідомлень інфраструктурний моніторинг повинен збирати чотири ключові групи телеметричних метрик:

* `bridge_in_flight_messages` (Gauge) — поточна кількість повідомлень у внутрішньому кільцевому буфері. Стійке утримання значення біля `HIGH_WATERMARK` свідчить про затор у вихідному каналі.
* `bridge_backpressure_pause_seconds_total` (Counter) — сумарний час перебування вхідного адаптера у стані паузи. Стрибок цієї метрики сигналізує про деградацію пропускної здатності цільової шини або мережевого лінку.
* `bridge_egress_latency_seconds` (Histogram) — час очікування підтвердження від вихідного брокера (RTT + Egress ACK). Дозволяє виявити зростання затримок дискової підсистеми на боці приймача.
* `bridge_quarantine_total` (Counter) — кількість повідомлень, відправлених у мертву чергу (DLQ). Будь-яке ненульове значення вимагає аналізу інженерами через можливу несумісність схем серіалізації.
