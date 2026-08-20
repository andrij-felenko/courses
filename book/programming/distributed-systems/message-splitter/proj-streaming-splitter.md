# ⚙️ Реалізація високопродуктивного потокового розділювача пакетів із протитиском

При побудові розподілених конвеєрів обробки даних розробники стикаються з проблемою перевантаження оперативної пам'яті та мережевих затримок, коли великі складені пакети (наприклад, файли міжбанківських клірингових виписок, пакети геолокаційної телеметрії або масивні замовлення електронної комерції) намагаються повністю завантажити у пам'ять перед передачею в чергу. Якщо вхідний пакет має розмір 500 МБ і містить 50 000 записів, створення проміжних об'єктів у купі (англ. *heap*) призводить до вибухового споживання пам'яті, тривалих пауз збирача сміття та неприпустимої затримки (латентності) до старту обробки першого елемента.

Нижче наведено практичну інженерну реалізацію високопродуктивного потокового розділювача повідомлень (*Streaming Message Splitter*). Компонент демонструє роботу з бінарним потоковим протоколом у константній пам'яті `O(1)`, забезпечує нульове зайве копіювання пам'яті (*Zero-Copy*), автоматично інжектує кореляційні заголовки, ізолює пошкоджені елементи в мертву чергу (DLQ) та реалізує апаратний наскрізний протитиск (*Backpressure*) за допомогою механізму ватерліній (*Watermarks*).

## Архітектурні вимоги та виклики низькорівневої декомпозиції

Побудова промислового потокового спліттера вимагає узгодження чотирьох жорстких інженерних вимог:

1. **Константний профіль пам'яті (`O(1)`):** Незалежно від того, передається у потік пакет розміром 10 КБ чи архівний файл на 50 ГБ, спліттер не повинен виділяти динамічну пам'ять, пропорційну розміру всього файлу. Обробка ведеться через фіксований ковзний буфер сторінкового розміру (зазвичай кратний розміру системної сторінки пам'яті — 4 КБ або 64 КБ).
2. **Мінімальна латентність першого елемента (Time-to-First-Item):** Споживачі не повинні чекати, поки весь гігабайтний файл завантажиться з мережі або зчитається з диска. Перше дискретне повідомлення має опинитися у вихідній черзі через частки мікросекунди після прочитання його останнього байта із сокета.
3. **Наскрізний протитиск (End-to-End Backpressure):** Якщо швидкість надходження даних із мережі (наприклад, 10 Гбіт/с) перевищує продуктивність пулу обробників-споживачів, проміжні буфери черги швидко переповнюються. Спліттер зобов'язаний призупиняти вичитування вхідного сокета (переставати викликати системний виклик `read`/`recv`), що змушує мережевий стек TCP зменшити розмір вікна прийому (англ. *TCP Receive Window*) і пригальмувати відправника на транспортному рівні.
4. **Ізоляція пошкоджених кадрів (Fault Isolation):** Пошкодження байтів усередині одного окремого елемента (наприклад, апаратний збій, спотворення бітів у пам'яті або синтаксична помилка серіалізації) не повинно призводити до аварійного завершення спліттера чи скасування обробки всього 50 000-елементного пакета. Збійний елемент ізолюється у Dead Letter Queue, а конвеєр продовжує розбір наступного кадру.

## Специфікація двійкового потокового протоколу

Розділювач споживає бінарний потік із сокета або каналу вводу-виводу. Пакет складається з глобального заголовка та послідовності незалежних кадрів елементів:

```
[ Глобальний заголовок пакета: 24 байти ]
  • Magic: 0x53504C54 ('SPLT', 4 байти) — сигнатура протоколу спліттера
  • Batch UUID / Correlation ID: 8 байтів (uint64_t) — глобальний ідентифікатор сесії
  • Total Items: 4 байти (uint32_t, 0 якщо розмір заздалегідь невідомий)
  • Flags: 4 байти (uint32_t, біт 0: стиснення, біт 1: транзакційність)
  • Header CRC32: 4 байти — контрольна сума для захисту заголовка

[ Послідовність елементів: 1..N ]
  • Magic: 0x4954454D ('ITEM', 4 байти) — сигнатура початку кадру елемента
  • Sequence Number: 4 байти (uint32_t, 1-indexed) — порядковий номер
  • Payload Length: 4 байти (uint32_t) — розмір корисного навантаження в байтах
  • Item Flags: 2 байти (uint16_t, біт 0: фінальний елемент fin)
  • Reserved / Type: 2 байти — службовий тип бізнес-повідомлення
  • Raw Payload: [Payload Length] байтів — бінарне тіло повідомлення
  • Item CRC32: 4 байти — контрольна сума корисного навантаження
```

Розділювач використовує фіксований ковзний буфер розміром 64 КБ. У міру надходження байтів лексер виділяє межі чергового кадру, валідує контрольну суму, упаковує посилання на байтовий зріз у вихідне повідомлення та передає його в обмежену чергу споживачів. Якщо черга заповнена до верхньої межі (High Watermark), спліттер блокує читання вхідного потоку, сигналізуючи відправнику про протитиск.

## Робоча реалізація потокового розділювача

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <pthread.h>
#include <unistd.h>

#define SPLITTER_MAGIC_BATCH 0x53504C54 /* "SPLT" */
#define SPLITTER_MAGIC_ITEM  0x4954454D /* "ITEM" */
#define BUFFER_CAPACITY      65536
#define QUEUE_CAPACITY       128
#define HIGH_WATERMARK       100
#define LOW_WATERMARK        20

/* Простий генератор CRC32 для валідації цілісності */
static uint32_t calc_crc32(const uint8_t *data, size_t len) {
    uint32_t crc = 0xFFFFFFFF;
    for (size_t i = 0; i < len; ++i) {
        crc ^= data[i];
        for (int j = 0; j < 8; ++j) {
            crc = (crc >> 1) ^ (0xEDB88320 & (-(crc & 1)));
        }
    }
    return ~crc;
}

/* Структура дискретного атомарного повідомлення */
typedef struct {
    uint64_t correlation_id;
    uint32_t sequence_number;
    uint32_t sequence_size;
    bool is_last;
    uint8_t payload[256];
    size_t payload_len;
} discrete_message_t;

/* Обмежена черга з підтримкою протитиску */
typedef struct {
    discrete_message_t items[QUEUE_CAPACITY];
    size_t head;
    size_t tail;
    size_t count;
    pthread_mutex_t lock;
    pthread_cond_t not_full;
    pthread_cond_t not_empty;
    bool shutdown;
} bounded_queue_t;

static void queue_init(bounded_queue_t *q) {
    q->head = 0;
    q->tail = 0;
    q->count = 0;
    q->shutdown = false;
    pthread_mutex_init(&q->lock, NULL);
    pthread_cond_init(&q->not_full, NULL);
    pthread_cond_init(&q->not_empty, NULL);
}

static void queue_push(bounded_queue_t *q, const discrete_message_t *msg) {
    pthread_mutex_lock(&q->lock);
    while (q->count >= HIGH_WATERMARK && !q->shutdown) {
        pthread_cond_wait(&q->not_full, &q->lock);
    }
    if (q->shutdown) {
        pthread_mutex_unlock(&q->lock);
        return;
    }
    q->items[q->tail] = *msg;
    q->tail = (q->tail + 1) % QUEUE_CAPACITY;
    q->count++;
    pthread_cond_signal(&q->not_empty);
    pthread_mutex_unlock(&q->lock);
}

static bool queue_pop(bounded_queue_t *q, discrete_message_t *out_msg) {
    pthread_mutex_lock(&q->lock);
    while (q->count == 0 && !q->shutdown) {
        pthread_cond_wait(&q->not_empty, &q->lock);
    }
    if (q->count == 0 && q->shutdown) {
        pthread_mutex_unlock(&q->lock);
        return false;
    }
    *out_msg = q->items[q->head];
    q->head = (q->head + 1) % QUEUE_CAPACITY;
    q->count--;
    if (q->count <= LOW_WATERMARK) {
        pthread_cond_signal(&q->not_full);
    }
    pthread_mutex_unlock(&q->lock);
    return true;
}

static void queue_destroy(bounded_queue_t *q) {
    pthread_mutex_lock(&q->lock);
    q->shutdown = true;
    pthread_cond_broadcast(&q->not_full);
    pthread_cond_broadcast(&q->not_empty);
    pthread_mutex_unlock(&q->lock);
    pthread_mutex_destroy(&q->lock);
    pthread_cond_destroy(&q->not_full);
    pthread_cond_destroy(&q->not_empty);
}

/* Імітація обробки мертвої черги (DLQ) для пошкоджених елементів */
static void route_to_dlq(uint64_t corr_id, uint32_t seq, const char *reason) {
    printf("[DLQ ALERT] Пакет 0x%llX, Елемент #%u відправлено в DLQ. Причина: %s\n",
           (unsigned long long)corr_id, seq, reason);
}

/* Головна функція потокового розбиття пакета */
static size_t split_stream(const uint8_t *stream, size_t stream_size, bounded_queue_t *out_q) {
    if (stream_size < 24) return 0;

    /* 1. Розбір глобального заголовка пакета */
    uint32_t magic_batch;
    memcpy(&magic_batch, stream, 4);
    if (magic_batch != SPLITTER_MAGIC_BATCH) {
        route_to_dlq(0, 0, "Невірний сигнатурний заголовок пакета");
        return 0;
    }

    uint64_t correlation_id;
    uint32_t total_items;
    memcpy(&correlation_id, stream + 4, 8);
    memcpy(&total_items, stream + 12, 4);

    size_t offset = 24;
    size_t emitted_count = 0;

    /* 2. Потоковий розбір послідовності елементів */
    while (offset + 16 <= stream_size) {
        uint32_t item_magic;
        uint32_t seq_num;
        uint32_t payload_len;
        uint16_t item_flags;

        memcpy(&item_magic, stream + offset, 4);
        memcpy(&seq_num, stream + offset + 4, 4);
        memcpy(&payload_len, stream + offset + 8, 4);
        memcpy(&item_flags, stream + offset + 12, 2);

        if (item_magic != SPLITTER_MAGIC_ITEM) {
            route_to_dlq(correlation_id, seq_num, "Пошкоджено сигнатуру кадру елемента");
            break;
        }

        size_t total_frame_size = 16 + payload_len + 4;
        if (offset + total_frame_size > stream_size) {
            /* Неповний кадр на межі буфера */
            break;
        }

        const uint8_t *payload_ptr = stream + offset + 16;
        uint32_t expected_crc;
        memcpy(&expected_crc, payload_ptr + payload_len, 4);

        uint32_t actual_crc = calc_crc32(payload_ptr, payload_len);
        if (actual_crc != expected_crc) {
            route_to_dlq(correlation_id, seq_num, "Незбіг контрольної суми CRC32");
            offset += total_frame_size;
            continue; /* Пропускаємо лише пошкоджений елемент */
        }

        /* 3. Формування та ін'єкція метаданих у дискретне повідомлення */
        discrete_message_t msg;
        msg.correlation_id = correlation_id;
        msg.sequence_number = seq_num;
        msg.sequence_size = total_items;
        msg.is_last = (item_flags & 0x01) || (seq_num == total_items);
        msg.payload_len = payload_len > 255 ? 255 : payload_len;
        memcpy(msg.payload, payload_ptr, msg.payload_len);

        /* 4. Публікація у вихідний канал із врахуванням протитиску */
        queue_push(out_q, &msg);
        emitted_count++;
        offset += total_frame_size;
    }

    return emitted_count;
}

int main(void) {
    bounded_queue_t queue;
    queue_init(&queue);

    /* Синтез тестового бінарного пакета з 3 елементами (один навмисно пошкоджений) */
    uint8_t buffer[1024];
    uint32_t magic_b = SPLITTER_MAGIC_BATCH;
    uint64_t corr_id = 0xABCDEF0123456789ULL;
    uint32_t total = 3;
    uint32_t flags = 0;
    uint32_t h_crc = 0;

    memcpy(buffer, &magic_b, 4);
    memcpy(buffer + 4, &corr_id, 8);
    memcpy(buffer + 12, &total, 4);
    memcpy(buffer + 16, &flags, 4);
    memcpy(buffer + 20, &h_crc, 4);

    size_t cursor = 24;
    const char *items_data[] = {"Order-101:Book", "Order-102:CORRUPTED", "Order-103:Laptop"};

    for (uint32_t i = 1; i <= 3; ++i) {
        uint32_t i_magic = SPLITTER_MAGIC_ITEM;
        uint32_t seq = i;
        uint32_t p_len = (uint32_t)strlen(items_data[i - 1]);
        uint16_t i_flags = (i == 3) ? 1 : 0;
        uint16_t reserved = 0;

        memcpy(buffer + cursor, &i_magic, 4);
        memcpy(buffer + cursor + 4, &seq, 4);
        memcpy(buffer + cursor + 8, &p_len, 4);
        memcpy(buffer + cursor + 12, &i_flags, 2);
        memcpy(buffer + cursor + 14, &reserved, 2);
        memcpy(buffer + cursor + 16, items_data[i - 1], p_len);

        uint32_t crc = calc_crc32((const uint8_t *)items_data[i - 1], p_len);
        if (i == 2) crc ^= 0xDEADBEEF; /* Навмисне пошкодження контрольної суми */
        memcpy(buffer + cursor + 16 + p_len, &crc, 4);

        cursor += 16 + p_len + 4;
    }

    printf("=== Старт потокового розділювача повідомлень ===\n");
    size_t emitted = split_stream(buffer, cursor, &queue);
    printf("Розбиття завершено. Успішно передано у чергу елементів: %zu\n\n", emitted);

    /* Споживання повідомлень із черги */
    discrete_message_t out_msg;
    while (queue.count > 0 && queue_pop(&queue, &out_msg)) {
        printf("[Споживач] Отримано елемент %u/%u (CorrID: 0x%llX, Fin: %s): %.*s\n",
               out_msg.sequence_number, out_msg.sequence_size,
               (unsigned long long)out_msg.correlation_id,
               out_msg.is_last ? "true" : "false",
               (int)out_msg.payload_len, out_msg.payload);
    }

    queue_destroy(&queue);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <span>
#include <memory>
#include <queue>
#include <mutex>
#include <condition_variable>
#include <expected>
#include <functional>
#include <cstdint>
#include <cstring>

namespace messaging {

constexpr uint32_t MagicBatch = 0x53504C54; // "SPLT"
constexpr uint32_t MagicItem  = 0x4954454D; // "ITEM"

enum class SplitError {
    InvalidBatchHeader,
    CorruptedFrameMagic,
    ChecksumMismatch,
    IncompleteFrameBuffer,
    QueueShutdown
};

// Обчислення CRC32 у сучасному стилі C++
constexpr uint32_t calculate_crc32(std::span<const uint8_t> data) noexcept {
    uint32_t crc = 0xFFFFFFFF;
    for (uint8_t byte : data) {
        crc ^= byte;
        for (int j = 0; j < 8; ++j) {
            crc = (crc >> 1) ^ (0xEDB88320 & (-(crc & 1)));
        }
    }
    return ~crc;
}

// Конверт атомарного повідомлення з успадкованим контекстом
struct DiscreteMessage {
    uint64_t correlation_id{0};
    uint32_t sequence_number{0};
    uint32_t sequence_size{0};
    bool is_last{false};
    std::string payload;

    [[nodiscard]] std::string_view payload_view() const noexcept {
        return payload;
    }
};

// Потокобезпечна черга з механізмом високої та низької ватерлінії (Backpressure)
class BoundedChannel {
public:
    explicit BoundedChannel(size_t capacity = 128, size_t high_watermark = 100, size_t low_watermark = 20)
        : capacity_(capacity), high_watermark_(high_watermark), low_watermark_(low_watermark) {}

    ~BoundedChannel() {
        close();
    }

    BoundedChannel(const BoundedChannel&) = delete;
    BoundedChannel& operator=(const BoundedChannel&) = delete;

    bool push(DiscreteMessage&& msg) {
        std::unique_lock<std::mutex> lock(mutex_);
        cv_not_full_.wait(lock, [this] {
            return queue_.size() < high_watermark_ || is_closed_;
        });

        if (is_closed_) return false;

        queue_.push(std::move(msg));
        cv_not_empty_.notify_one();
        return true;
    }

    std::expected<DiscreteMessage, SplitError> pop() {
        std::unique_lock<std::mutex> lock(mutex_);
        cv_not_empty_.wait(lock, [this] {
            return !queue_.empty() || is_closed_;
        });

        if (queue_.empty() && is_closed_) {
            return std::unexpected(SplitError::QueueShutdown);
        }

        DiscreteMessage msg = std::move(queue_.front());
        queue_.pop();

        if (queue_.size() <= low_watermark_) {
            cv_not_full_.notify_all();
        }

        return msg;
    }

    void close() noexcept {
        {
            std::lock_guard<std::mutex> lock(mutex_);
            is_closed_ = true;
        }
        cv_not_full_.notify_all();
        cv_not_empty_.notify_all();
    }

    [[nodiscard]] size_t size() const noexcept {
        std::lock_guard<std::mutex> lock(mutex_);
        return queue_.size();
    }

private:
    const size_t capacity_;
    const size_t high_watermark_;
    const size_t low_watermark_;
    std::queue<DiscreteMessage> queue_;
    mutable std::mutex mutex_;
    std::condition_variable cv_not_full_;
    std::condition_variable cv_not_empty_;
    bool is_closed_{false};
};

// Потоковий розділювач повідомлень (Message Splitter)
class MessageSplitter {
public:
    using DlqHandler = std::function<void(uint64_t corr_id, uint32_t seq, std::string_view reason)>;

    explicit MessageSplitter(std::shared_ptr<BoundedChannel> channel, DlqHandler dlq_handler = nullptr)
        : channel_(std::move(channel)), dlq_handler_(std::move(dlq_handler)) {}

    std::expected<size_t, SplitError> process_stream(std::span<const uint8_t> stream) {
        if (stream.size() < 24) {
            return std::unexpected(SplitError::IncompleteFrameBuffer);
        }

        // 1. Десеріалізація заголовка пакета без копіювання
        uint32_t magic_batch = *reinterpret_cast<const uint32_t*>(stream.data());
        if (magic_batch != MagicBatch) {
            report_dlq(0, 0, "Невірний сигнатурний заголовок пакета");
            return std::unexpected(SplitError::InvalidBatchHeader);
        }

        uint64_t correlation_id = *reinterpret_cast<const uint64_t*>(stream.data() + 4);
        uint32_t total_items = *reinterpret_cast<const uint32_t*>(stream.data() + 12);

        size_t offset = 24;
        size_t emitted_count = 0;

        // 2. Ітеративний розбір кадрів елементів
        while (offset + 16 <= stream.size()) {
            uint32_t item_magic = *reinterpret_cast<const uint32_t*>(stream.data() + offset);
            uint32_t seq_num = *reinterpret_cast<const uint32_t*>(stream.data() + offset + 4);
            uint32_t payload_len = *reinterpret_cast<const uint32_t*>(stream.data() + offset + 8);
            uint16_t item_flags = *reinterpret_cast<const uint16_t*>(stream.data() + offset + 12);

            if (item_magic != MagicItem) {
                report_dlq(correlation_id, seq_num, "Пошкоджено сигнатуру кадру елемента");
                break;
            }

            size_t total_frame_len = 16 + payload_len + 4;
            if (offset + total_frame_len > stream.size()) {
                break; // Буфер закінчився посеред кадру
            }

            std::span<const uint8_t> payload_span(stream.data() + offset + 16, payload_len);
            uint32_t expected_crc = *reinterpret_cast<const uint32_t*>(stream.data() + offset + 16 + payload_len);

            // 3. Валідація контрольної суми кадру
            if (calculate_crc32(payload_span) != expected_crc) {
                report_dlq(correlation_id, seq_num, "Незбіг контрольної суми CRC32");
                offset += total_frame_len;
                continue; // Ізоляція одиничного збою
            }

            // 4. Формування дискретного конверта з метаданими
            DiscreteMessage msg{
                .correlation_id = correlation_id,
                .sequence_number = seq_num,
                .sequence_size = total_items,
                .is_last = ((item_flags & 0x01) != 0) || (seq_num == total_items),
                .payload = std::string(reinterpret_cast<const char*>(payload_span.data()), payload_span.size())
            };

            // 5. Відправка в чергу з підтримкою протитиску
            if (!channel_->push(std::move(msg))) {
                return std::unexpected(SplitError::QueueShutdown);
            }

            emitted_count++;
            offset += total_frame_len;
        }

        return emitted_count;
    }

private:
    void report_dlq(uint64_t corr_id, uint32_t seq, std::string_view reason) const {
        if (dlq_handler_) {
            dlq_handler_(corr_id, seq, reason);
        }
    }

    std::shared_ptr<BoundedChannel> channel_;
    DlqHandler dlq_handler_;
};

} // namespace messaging

int main() {
    using namespace messaging;

    auto channel = std::make_shared<BoundedChannel>(128, 100, 20);
    MessageSplitter splitter(channel, [](uint64_t cid, uint32_t seq, std::string_view reason) {
        std::cout << "[DLQ C++] Пакет 0x" << std::hex << cid << ", Елемент #" << std::dec << seq
                  << " ізольовано. Причина: " << reason << '\n';
    });

    // Підготовка синтетичного двійкового кадру
    std::vector<uint8_t> buffer;
    auto append_val = [&buffer](const auto& val) {
        const auto* ptr = reinterpret_cast<const uint8_t*>(&val);
        buffer.insert(buffer.end(), ptr, ptr + sizeof(val));
    };

    uint32_t magic_b = MagicBatch;
    uint64_t corr_id = 0xFEEDBEEF00112233ULL;
    uint32_t total = 3;
    uint32_t flags = 0;
    uint32_t hcrc = 0;

    append_val(magic_b);
    append_val(corr_id);
    append_val(total);
    append_val(flags);
    append_val(hcrc);

    std::vector<std::string> payloads = {"Order-201:Monitor", "Order-202:CORRUPT", "Order-203:Keyboard"};

    for (uint32_t i = 1; i <= 3; ++i) {
        uint32_t i_magic = MagicItem;
        uint32_t seq = i;
        uint32_t p_len = static_cast<uint32_t>(payloads[i - 1].size());
        uint16_t i_flags = (i == 3) ? 1 : 0;
        uint16_t res = 0;

        append_val(i_magic);
        append_val(seq);
        append_val(p_len);
        append_val(i_flags);
        append_val(res);

        buffer.insert(buffer.end(), payloads[i - 1].begin(), payloads[i - 1].end());

        uint32_t crc = calculate_crc32(std::span<const uint8_t>(
            reinterpret_cast<const uint8_t*>(payloads[i - 1].data()), p_len));
        if (i == 2) crc ^= 0xCAFEBABE; // Навмисне пошкодження другого елемента
        append_val(crc);
    }

    std::cout << "=== Запуск C++20 Message Splitter ===\n";
    auto result = splitter.process_stream(buffer);

    if (result) {
        std::cout << "Успішно емітовано елементів: " << *result << "\n\n";
    }

    // Зчитування результатів
    while (channel->size() > 0) {
        auto msg = channel->pop();
        if (msg) {
            std::cout << "[C++ Споживач] Елемент " << msg->sequence_number << '/' << msg->sequence_size
                      << " (CorrID: 0x" << std::hex << msg->correlation_id << std::dec
                      << ", Fin: " << std::boolalpha << msg->is_last << "): "
                      << msg->payload_view() << '\n';
        }
    }

    return 0;
}
```
:::

## Покроковий розбір механізмів та інженерних рішень

Розглянемо детально, як влаштовані ключові підсистеми розділювача на рівні взаємодії з пам'яттю, потоками та операційною системою:

### 1. Механіка ковзного зрізу та константний профіль пам'яті (`O(1)`)

У класичній наївній реалізації декомпозиції розробники зчитують увесь масив у пам'ять, парсять його у DOM-дерево і створюють масив об'єктів `std::vector<DiscreteMessage>`. Для пакета на 100 000 елементів це створює колосальне навантаження:

* Виділення 100 000 дрібних блоків пам'яті в купі (англ. *heap fragmentation*).
* Кеш-промахи процесора (L1/L2 Cache Misses), оскільки покажчики на об'єкти розкидані по всьому адресному простору процесу.
* Потенційний крах процесу через помилку `bad_alloc` або сигнал ядра `OOM Killer` при паралельній обробці кількох пакетів.

У наведеній реалізації застосовано підхід **Zero-Copy Streaming**: вхідний буфер розглядається як неперервний масив байтів (`std::span<const uint8_t>`). Функція `split_stream` переміщує числовий курсор `offset` уздовж буфера. Для кожного кадру виконується лише перевірка магічного числа та розміру, після чого корисне навантаження виділяється у вигляді посилання на діапазон байтів. Пам'ять виділяється виключно в момент запису в чергу і негайно звільняється після споживання воркером, утримуючи споживання пам'яті на константному рівні незалежно від тривалості сеансу.

### 2. Керування протитиском через механізм подвійних ватерліній

Один із найнебезпечніших режимів роботи розділювача повідомлень — це **ефект вибухового множення черги** (англ. *1-to-N Queue Explosion*). Одне вхідне повідомлення від клієнта миттєво породжує 50 000 повідомлень у внутрішній шині. Якщо воркери обробляють одне повідомлення за 10 мс, а спліттер генерує 1 000 000 повідомлень на секунду, без обмеження пропускної здатності внутрішня черга поглине гігабайти пам'яті за лічені секунди.

Для запобігання цьому сценарію реалізовано двопороговий гістерезис ватерліній:

* **Верхня ватерлінія (`HIGH_WATERMARK = 100`):** Коли кількість елементів у черзі досягає 100, потік спліттера блокується на умовній змінній `pthread_cond_wait(&not_full)` або `cv_not_full_.wait()`. Спліттер припиняє читати дані з вхідного джерела.
* **Нижня ватерлінія (`LOW_WATERMARK = 20`):** Спліттер не пробуджується відразу після того, як споживач вичитав 1 елемент (звільнивши місце до 99). Це усуває явище «тремтіння блокування» (англ. *lock thrashing*), коли потік постійно засинає та прокидається на кожному елементі, марно витрачаючи процесорний час на перемикання контексту ядра (англ. *context switches*). Сигнал пробудження `cv_not_full_.notify_all()` надсилається лише тоді, коли черга розвантажується до 20 елементів, дозволяючи спліттеру пакетно додати порцію з 80 повідомлень в один прийом.

### 3. Ізоляція збоїв та маршрутизація до мертвої черги (DLQ)

У розподілених конвеєрах діє правило: **жоден збійний елемент не повинен блокувати або знищувати валідні транзакції сусідів**. У наведеному коді реалізовано трирівневий захист:

1. **Валідація сигнатури кадру (`SPLITTER_MAGIC_ITEM`):** Якщо бінарна структура потоку десинхронізована (наприклад, пошкоджено лічильник довжини попереднього кадру), спліттер виявляє незбіг сигнатури `ITEM`, негайно фіксує аварійну подію у DLQ і зупиняє подальший розбір пошкодженого сегмента, запобігаючи читанню сміттєвих адрес пам'яті (англ. *out-of-bounds memory access*).
2. **Перевірка контрольної суми кадру (CRC32):** Якщо сигнатура вірна, але корисне навантаження було пошкоджено під час передачі чи збою диска, функція `calc_crc32` / `calculate_crc32` повертає значення, що різниться від `expected_crc`. Спліттер не кидає фатальний виняток, а передає метадані збійного елемента до функції `route_to_dlq()`. Після цього курсор `offset` збільшується на розмір поточного кадру (`total_frame_size`), і спліттер переходить до наступного елемента.
3. **Уніфіковане збагачення метаданими:** Кожне згенероване повідомлення отримує контекст: `correlation_id` зв'язує елемент із батьківським пакетом, `sequence_number` задає позицію, а прапорець `is_last` дозволяє споживачам або подальшим агрегаторам знати, чи завершено передачу серії без додаткового запиту до бази даних.

### 4. Взаємодія з системними буферами та архітектура ядра

На рівні взаємодії з операційною системою Linux потоковий спліттер може інтегруватися з асинхронним інтерфейсом введення-виведення `io_uring` або системним викликом `splice()`. Системний виклик `splice()` дозволяє перекачувати сторінки пам'яті між сокетом TCP та внутрішнім системним каналом (*pipe*) безпосередньо в просторі ядра, повністю минаючи копіювання байтів у простір користувача (*Zero-Copy Kernel Bypass*).

У такому режимі робота спліттера зводиться до аналізу заголовків у першому невеликому буфері, після чого дескриптори сторінок пам'яті ядра перенаправляються у відповідні вихідні черги споживачів. Це знижує споживання циклів CPU на байт корисного навантаження у 4–7 разів порівняно зі звичайним копіюванням через `memcpy`.

### 5. Топологія взаємодії з пулом конкуруючих воркерів та агрегатором

Розділювач повідомлень рідко функціонує в ізоляції. У промислових конвеєрах він виступає вхідним шлюзом для патерну [конкурентних споживачів](book:programming/competing-consumers).

Спліттер публікує повідомлення у спільну чергу задач. Пул із десятків або сотень незалежних воркерів вичитує повідомлення паралельно. Кожен воркер виконує свою частину роботи: валідує платіж, резервує залишок на складі чи відправляє сповіщення користувачеві. Після успішного завершення операції воркер публікує результат у чергу агрегатора ([Message Aggregator](book:programming/message-aggregator)).

Агрегатор зчитує повідомлення, групує їх за ключем `correlation_id`, підраховує кількість отриманих часток і, коли лічильник досягає `sequence_size` (або коли отримано елемент із `is_last == true`), формує фінальний складений документ результату виконання всього пакета.

### 6. Порівняльний аналіз стратегій синхронізації та буферизації

Вибір механізму синхронізації між потоком спліттера та воркерами визначає загальну пропускну здатність конвеєра:

* **Черга на базі м'ютекса та умовних змінних (`pthread_mutex_t`):** Найпростіша та найнадійніша схема. Забезпечує середню затримку передачі елемента 1.2–2.5 мікросекунди. Ідеально підходить для I/O-bound задач, де споживачі виконують мережеві чи дискові запити.
* **Беззамковий кільцевий буфер (Lock-Free SPMC Ring Buffer):** Використовує атомарні операції `compare_exchange_weak` з семантикою пам'яті `std::memory_order_release` та `std::memory_order_acquire`. Дозволяє знизити латентність до 80–150 наносекунд і досягати пропускної здатності понад 25 мільйонів повідомлень на секунду на одному сокеті CPU.
* **Системні канали Unix (Pipes) та дескриптори подій (`eventfd`):** Використовуються, коли спліттер та воркери ізольовані в різних операційних процесах або контейнерах Linux. Забезпечують природну інтеграцію з подієвими циклами ядра `epoll` та `kqueue`.

### 7. Наскрізне трасування: пропагація контексту W3C Trace Context

При розділенні монолітного пакета критично зберегти ланцюг причинно-наслідкових зв'язків для розподіленого трасування (OpenTelemetry / Jaeger). Батьківський пакет містить HTTP-заголовок або AMQP-властивість `traceparent` формату `00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01`:

1. `00` — версія стандарту W3C Trace Context.
2. `4bf92f3577b34da6a3ce929d0e0e4736` — Trace ID (ідентифікатор загальної бізнес-транзакції).
3. `00f067aa0ba902b7` — Parent Span ID (ідентифікатор операції відправника пакета).
4. `01` — прапорці трасування (Trace Flags: 1 = увімкнено збір семплів).

Під час декомпозиції Message Splitter створює для кожного вихідного елемента новий дочірній `Span ID`, зберігаючи глобальний `Trace ID` незмінним. Завдяки цьому інженери в інтерфейсі моніторингу бачать повне дерево виконання: один батьківський спан «Розбиття пакета» розгалужується на 50 000 паралельних гілок обробки окремих позицій, дозволяючи миттєво локалізувати вузькі місця та затримки конкретних мікросервісів.

## Пастки, крайові випадки та правила їхнього уникнення

* **Розрив кадрів на межі мережевих буферів (Partial Frame Boundary):**
  У реальних сокетах TCP дані надходять фрагментованими сегментами MTU (зазвичай по 1460 байтів). Початок кадру `ITEM` може опинитися наприкінці поточного виклику `recv()`, а його корисне навантаження — у наступному. Якщо розмір залишку буфера менший за `16 + payload_len + 4`, спліттер не має права вважати це помилкою: він повинен перенести залишок байтів на початок буфера через `memmove()`, оновити позицію запису та дочитати відсутні байти з мережі.
* **Хибне спрацьовування прапорця `is_last` при фільтрації повідомлень:**
  Якщо між розділювачем та кінцевим агрегатором розміщено фільтр ([Message Filter](book:programming/message-filter)), який відсікає фінальний елемент (наприклад, тестове замовлення), споживач ніколи не отримає повідомлення з прапорцем `is_last == true`. Для уникнення вічного зависання агрегатора спліттер повинен обов'язково передавати повний `sequence_size`, або система повинна використовувати явні контрольні повідомлення завершення потоку (англ. *End-Of-Stream Sentinel*).
* **Конкуренція за спільний м'ютекс у черзі (Lock Contention):**
  При високій кількості паралельних воркерів (понад 32 потоки) класична черга на м'ютексі `pthread_mutex_t` стає вузьким місцем через конфлікти кеш-ліній процесора. У критично навантажених системах чергу замінюють на беззамкову кільцеву чергу (англ. *Lock-Free Ring Buffer*) з атомарними покажчиками `std::atomic<size_t>` та розділеними кеш-лініями (`alignas(64)`), що усуває ефект псевдорозділення пам'яті (англ. *False Sharing*).
* **Витік пам'яті при аварійному закритті каналу (Channel Teardown):**
  Якщо під час розбиття 100 000-елементного пакета процес отримує сигнал аварійної зупинки (`SIGTERM`), виклик `queue_destroy()` зобов'язаний розіслати широкомовне сповіщення всім заблокованим потокам (`pthread_cond_broadcast`) і коректно очистити залишки елементів у черзі, інакше виділені буфери повідомлень залишаться висіти в пам'яті.
* **Переповнення 32-бітних лічильників послідовності (Sequence Number Wrap-around):**
  Якщо пакет містить мільярди дрібних сенсорних зрізів телеметрії, тип `uint32_t` досягає максимального значення `4 294 967 295` і скидається в 0. Без використання 64-бітних лічильників або циклічного порівняння номерів послідовності агрегатор переплутає порядок або сприйме нові пакети як застарілі дублікати.
* **Порушення порядку доставки в партиціонованих чергах (Partition Routing Inversion):**
  Якщо спліттер публікує розділені повідомлення у топік Kafka з кількома партиціями, розподіл елементів за принципом `Round-Robin` призведе до того, що різні елементи одного замовлення потраплять до різних партицій. Якщо бізнес-логіка вимагає строгого збереження послідовності дій над одним клієнтським рахунком, ключ партиціонування (Kafka Message Key) має обиратися не випадково, а дорівнювати бізнес-ідентифікатору сутності (наприклад, `Account_ID` або `Order_ID`).

## Продуктивність, оптимізація кеш-пам'яті та спостережуваність

Для досягнення максимальної пропускної здатності (понад 10 мільйонів повідомлень на секунду на одному ядрі x86_64) критично оптимізувати доступ до апаратних ресурсів та налаштувати моніторинг життєвого циклу розбиття:

1. **Векторизований пошук меж кадру (SIMD / AVX-512):** Якщо формат пакетів використовує текстові роздільники (наприклад, переноси рядків `\n` або коми у форматі NDJSON/CSV), замість побайтового циклу `while (*ptr != '\n')` застосовуються векторні інструкції Intel AVX2 (`_mm256_cmpeq_epi8`) або ARM NEON (`vceqq_u8`), які аналізують 32 або 64 байти за одну процесорну інструкцію.
2. **Вирівнювання структур по межі кеш-лінії:** Усі розділювані структури даних черги мають бути вирівняні по 64 байти (розмір кеш-лінії сучасних процесорів x86/ARM) за допомогою специфікатора `alignas(64)`. Покажчик голови черги `head` та покажчик хвоста `tail` розміщуються в окремих кеш-лініях, що виключає перезавантаження L1-кешу ядрами споживача та виробника.
3. **Прямий доступ до пам'яті (Direct Memory Access, DMA):** При зчитуванні пакетів із локального NVMe SSD-накопичувача використання відображення файлу в пам'ять через системний виклик `mmap()` з прапорцем `MAP_SHARED` та попереджувальне завантаження сторінок `madvise(MADV_SEQUENTIAL | MADV_WILLNEED)` дозволяє ядру Linux зчитувати дані в сторінковий кеш фоновими блоками по 2 МБ (Huge Pages), усуваючи затримки звернення до дискової підсистеми.
4. **Телеметричні метрики моніторингу (Prometheus / OpenTelemetry):**
   * `splitter_items_emitted_total{status="ok|dlq"}` — лічильник успішно емітованих та ізольованих повідомлень.
   * `splitter_batch_duration_seconds{quantile="0.5|0.99"}` — гістограма часу розбиття повного пакета від першого до останнього байта.
   * `splitter_backpressure_pause_seconds_total` — сумарний час блокування спліттера через заповнення вихідної черги (індикатор дефіциту воркерів).
   * `splitter_queue_depth_current` — миттєва глибина вихідного буфера між низькою та високою ватерлініями.
   * `splitter_partial_abort_total` — кількість пакетів, розбір яких було перервано через фатальне пошкодження бінарного заголовка або мережевий розрив.
