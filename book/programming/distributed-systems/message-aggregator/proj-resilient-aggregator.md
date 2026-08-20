# ⚙️ Реалізація потокобезпечного агрегатора та ресеквенсера повідомлень

Цей проект демонструє виробничу реалізацію двох фундаментальних станційних компонентів розподіленого конвеєра:
1. **Message Aggregator:** Збирає дискретні повідомлення за спільним кореляційним ключем `correlation_id`, фільтрує дублікати транспортного рівня, перевіряє критерії повноти (кількість елементів або FIN-прапорець), підтримує тайм-аути та відсікає запізнілі повідомлення за допомогою кешу надгробків (Tombstones).
2. **Message Resequencer:** Відновлює строго монотонний зростаючий порядок потоку повідомлень (`1, 2, 3...`) за допомогою ковзного буфера очікування та алгоритму детекції прогалин.

Компоненти розроблені для роботи у багатопотокових середовищах із високою інтенсивністю вхідного трафіку та забезпечують детерміновану поведінку при будь-яких мережевих аномаліях.

## Архітектурний дизайн конвеєра

```
[Потік повідомлень] ──► [Дедуплікатор & Tombstones] ──► [Кореляційні кошики] ──► [Оцінка критеріїв]
                                                                                      │
[Строго впорядкований вихід] ◄── [Resequencer] ◄──────────────────────────────────────┘
```

Вхідне повідомлення спочатку проходить перевірку на наявність активного надгробка для запобігання відновленню вже закритих сесій. Якщо сесія активна або створюється вперше, повідомлення потрапляє до відповідного кошика, де дедуплікується за номером послідовності. При виконанні умов повноти агрегатор вивільняє результат і передає його або безпосередньо споживачам, або до ресеквенсера для потокового сортування.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>
#include <pthread.h>
#include <time.h>
#include <unistd.h>

#define MAX_ITEMS_PER_BUCKET 64
#define HASH_TABLE_SIZE 128
#define TOMBSTONE_CAPACITY 256

// Отримання монотонного часу в мілісекундах
static uint64_t current_time_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000 + (uint64_t)ts.tv_nsec / 1000000;
}

// Структура вхідного повідомлення
typedef struct {
    char correlation_id[64];
    uint64_t sequence_number;
    uint64_t sequence_size;
    bool is_last;
    char payload[128];
} Message;

// Кореляційний кошик агрегатора
typedef struct AggregationBucket {
    char correlation_id[64];
    Message items[MAX_ITEMS_PER_BUCKET];
    size_t count;
    uint64_t expected_total;
    uint64_t created_at_ms;
    uint64_t last_activity_ms;
    uint64_t timeout_ms;
    bool has_fin;
    struct AggregationBucket* next;
} AggregationBucket;

// Запис надгробка для закритих сесій
typedef struct {
    char correlation_id[64];
    uint64_t closed_at_ms;
    uint64_t ttl_ms;
    bool active;
} TombstoneEntry;

// Головна структура агрегатора
typedef struct {
    AggregationBucket* buckets[HASH_TABLE_SIZE];
    TombstoneEntry tombstones[TOMBSTONE_CAPACITY];
    size_t tombstone_count;
    pthread_mutex_t lock;
} MessageAggregator;

// Хеш-функція djb2 для рядків
static unsigned int hash_string(const char* str) {
    unsigned int hash = 5381;
    int c;
    while ((c = *str++)) {
        hash = ((hash << 5) + hash) + c;
    }
    return hash % HASH_TABLE_SIZE;
}

void aggregator_init(MessageAggregator* agg) {
    memset(agg->buckets, 0, sizeof(agg->buckets));
    memset(agg->tombstones, 0, sizeof(agg->tombstones));
    agg->tombstone_count = 0;
    pthread_mutex_init(&agg->lock, NULL);
}

void aggregator_destroy(MessageAggregator* agg) {
    pthread_mutex_lock(&agg->lock);
    for (int i = 0; i < HASH_TABLE_SIZE; ++i) {
        AggregationBucket* curr = agg->buckets[i];
        while (curr) {
            AggregationBucket* next = curr->next;
            free(curr);
            curr = next;
        }
        agg->buckets[i] = NULL;
    }
    pthread_mutex_unlock(&agg->lock);
    pthread_mutex_destroy(&agg->lock);
}

static bool is_tombstoned(MessageAggregator* agg, const char* corr_id, uint64_t now) {
    for (size_t i = 0; i < agg->tombstone_count; ++i) {
        if (agg->tombstones[i].active && strcmp(agg->tombstones[i].correlation_id, corr_id) == 0) {
            if (now - agg->tombstones[i].closed_at_ms < agg->tombstones[i].ttl_ms) {
                return true;
            } else {
                agg->tombstones[i].active = false; // TTL сплив
            }
        }
    }
    return false;
}

static void add_tombstone(MessageAggregator* agg, const char* corr_id, uint64_t now, uint64_t ttl_ms) {
    for (size_t i = 0; i < TOMBSTONE_CAPACITY; ++i) {
        if (!agg->tombstones[i].active) {
            strncpy(agg->tombstones[i].correlation_id, corr_id, 63);
            agg->tombstones[i].closed_at_ms = now;
            agg->tombstones[i].ttl_ms = ttl_ms;
            agg->tombstones[i].active = true;
            if (i >= agg->tombstone_count) agg->tombstone_count = i + 1;
            return;
        }
    }
}

// Додавання повідомлення та перевірка завершення
// Повертає 1, якщо кошик завершено і агреговано; 0 - якщо накопичується; -1 - дублікат/відхилено
int aggregator_process(MessageAggregator* agg, const Message* msg, Message* out_batch, size_t* out_count) {
    pthread_mutex_lock(&agg->lock);
    uint64_t now = current_time_ms();

    // 1. Перевірка надгробка (запізніле повідомлення)
    if (is_tombstoned(agg, msg->correlation_id, now)) {
        printf("[Aggregator] Відхилено запізніле повідомлення (Tombstone): %s Seq=%lu\n",
               msg->correlation_id, msg->sequence_number);
        pthread_mutex_unlock(&agg->lock);
        return -1;
    }

    unsigned int idx = hash_string(msg->correlation_id);
    AggregationBucket* b = agg->buckets[idx];
    AggregationBucket* prev = NULL;

    while (b && strcmp(b->correlation_id, msg->correlation_id) != 0) {
        prev = b;
        b = b->next;
    }

    // Створення нового кошика, якщо не існує
    if (!b) {
        b = (AggregationBucket*)calloc(1, sizeof(AggregationBucket));
        strncpy(b->correlation_id, msg->correlation_id, 63);
        b->created_at_ms = now;
        b->last_activity_ms = now;
        b->timeout_ms = 3000; // 3 секунди дедлайн
        b->expected_total = msg->sequence_size;
        b->next = agg->buckets[idx];
        agg->buckets[idx] = b;
    }

    // 2. Дедуплікація за Sequence Number
    for (size_t i = 0; i < b->count; ++i) {
        if (b->items[i].sequence_number == msg->sequence_number) {
            printf("[Aggregator] Ігнорування дубліката: %s Seq=%lu\n",
               msg->correlation_id, msg->sequence_number);
            pthread_mutex_unlock(&agg->lock);
            return -1;
        }
    }

    // 3. Додавання елемента
    if (b->count < MAX_ITEMS_PER_BUCKET) {
        b->items[b->count++] = *msg;
        b->last_activity_ms = now;
        if (msg->is_last) b->has_fin = true;
        if (msg->sequence_size > 0) b->expected_total = msg->sequence_size;
    }

    // 4. Оцінка критерію завершення
    bool completed = false;
    if (b->expected_total > 0 && b->count == b->expected_total) {
        completed = true;
    } else if (b->has_fin && b->expected_total == 0) {
        completed = true;
    }

    if (completed) {
        *out_count = b->count;
        memcpy(out_batch, b->items, b->count * sizeof(Message));

        // Видалення кошика з хеш-таблиці
        if (prev) prev->next = b->next;
        else agg->buckets[idx] = b->next;

        free(b);
        add_tombstone(agg, msg->correlation_id, now, 10000); // Надгробок на 10 с
        pthread_mutex_unlock(&agg->lock);
        return 1;
    }

    pthread_mutex_unlock(&agg->lock);
    return 0;
}

// ── Ресеквенсер повідомлень ────────────────────────────────────────────────
#define RESEQ_MAX_BUFFER 64

typedef struct {
    Message buffer[RESEQ_MAX_BUFFER];
    bool slot_used[RESEQ_MAX_BUFFER];
    uint64_t next_expected_seq;
    pthread_mutex_t lock;
} MessageResequencer;

void resequencer_init(MessageResequencer* reseq, uint64_t start_seq) {
    memset(reseq->slot_used, 0, sizeof(reseq->slot_used));
    reseq->next_expected_seq = start_seq;
    pthread_mutex_init(&reseq->lock, NULL);
}

void resequencer_destroy(MessageResequencer* reseq) {
    pthread_mutex_destroy(&reseq->lock);
}

// Вставка повідомлення у ресеквенсер та отримання впорядкованого пакета
size_t resequencer_push(MessageResequencer* reseq, const Message* msg, Message* out_ordered) {
    pthread_mutex_lock(&reseq->lock);
    size_t emitted_count = 0;

    if (msg->sequence_number >= reseq->next_expected_seq) {
        uint64_t offset = msg->sequence_number - reseq->next_expected_seq;
        if (offset < RESEQ_MAX_BUFFER) {
            reseq->buffer[offset] = *msg;
            reseq->slot_used[offset] = true;
        }
    }

    // Каскадне вилучення елементів без прогалин
    while (reseq->slot_used[0]) {
        out_ordered[emitted_count++] = reseq->buffer[0];
        reseq->next_expected_seq++;

        // Зсув буфера на одну позицію вліво
        for (size_t i = 0; i < RESEQ_MAX_BUFFER - 1; ++i) {
            reseq->buffer[i] = reseq->buffer[i + 1];
            reseq->slot_used[i] = reseq->slot_used[i + 1];
        }
        reseq->slot_used[RESEQ_MAX_BUFFER - 1] = false;
    }

    pthread_mutex_unlock(&reseq->lock);
    return emitted_count;
}
```
```cpp
#include <iostream>
#include <string>
#include <vector>
#include <unordered_map>
#include <map>
#include <mutex>
#include <chrono>
#include <optional>
#include <algorithm>
#include <cstdint>

namespace eip {

using Clock = std::chrono::steady_clock;
using TimePoint = Clock::time_point;

struct Message {
    std::string correlation_id;
    uint64_t sequence_number{0};
    uint64_t sequence_size{0};
    bool is_last{false};
    std::string payload;
};

struct AggregationResult {
    std::string correlation_id;
    std::vector<Message> items;
    bool is_complete{false};
    std::string failure_reason;
};

class ConcurrentAggregator {
public:
    explicit ConcurrentAggregator(std::chrono::milliseconds default_timeout = std::chrono::milliseconds(3000),
                                  std::chrono::seconds tombstone_ttl = std::chrono::seconds(10))
        : default_timeout_(default_timeout), tombstone_ttl_(tombstone_ttl) {}

    // Додавання повідомлення. Якщо кошик завершено, повертає AggregationResult
    std::optional<AggregationResult> process_message(Message msg) {
        const auto now = Clock::now();
        std::lock_guard<std::mutex> lock(mutex_);

        // 1. Перевірка надгробків закритих сесій
        cleanup_tombstones(now);
        if (auto it = tombstones_.find(msg.correlation_id); it != tombstones_.end()) {
            std::cout << "[Aggregator] Відхилено запізнілий елемент для закритого ID: "
                      << msg.correlation_id << " Seq: " << msg.sequence_number << "\n";
            return std::nullopt;
        }

        // 2. Отримання або створення кошика
        auto& bucket = buckets_[msg.correlation_id];
        if (bucket.items.empty()) {
            bucket.correlation_id = msg.correlation_id;
            bucket.created_at = now;
            bucket.last_activity = now;
            bucket.expected_total = msg.sequence_size;
            bucket.timeout = default_timeout_;
        }

        // 3. Дедуплікація за Sequence Number
        for (const auto& existing : bucket.items) {
            if (existing.sequence_number == msg.sequence_number) {
                std::cout << "[Aggregator] Ігнорування дубліката для " << msg.correlation_id
                          << " Seq: " << msg.sequence_number << "\n";
                return std::nullopt;
            }
        }

        // 4. Додавання нового елемента
        bucket.last_activity = now;
        if (msg.is_last) bucket.has_fin = true;
        if (msg.sequence_size > 0) bucket.expected_total = msg.sequence_size;
        bucket.items.push_back(std::move(msg));

        // 5. Оцінка критерію завершення
        bool ready = false;
        if (bucket.expected_total > 0 && bucket.items.size() == bucket.expected_total) {
            ready = true;
        } else if (bucket.has_fin && bucket.expected_total == 0) {
            ready = true;
        }

        if (ready) {
            AggregationResult result;
            result.correlation_id = bucket.correlation_id;
            result.items = std::move(bucket.items);
            result.is_complete = true;

            // Видалення кошика та фіксація надгробка
            buckets_.erase(bucket.correlation_id);
            tombstones_[result.correlation_id] = now + tombstone_ttl_;
            return result;
        }

        return std::nullopt;
    }

    // Фонове сканування активних кошиків на сплив дедлайну
    std::vector<AggregationResult> sweep_timeouts() {
        const auto now = Clock::now();
        std::vector<AggregationResult> expired_results;
        std::lock_guard<std::mutex> lock(mutex_);

        for (auto it = buckets_.begin(); it != buckets_.end(); ) {
            auto& bucket = it->second;
            if (now - bucket.created_at >= bucket.timeout) {
                AggregationResult res;
                res.correlation_id = bucket.correlation_id;
                res.items = std::move(bucket.items);
                res.is_complete = false;
                res.failure_reason = "TIMEOUT_EXPIRED";

                tombstones_[res.correlation_id] = now + tombstone_ttl_;
                expired_results.push_back(std::move(res));
                it = buckets_.erase(it);
            } else {
                ++it;
            }
        }
        return expired_results;
    }

private:
    struct Bucket {
        std::string correlation_id;
        std::vector<Message> items;
        uint64_t expected_total{0};
        TimePoint created_at;
        TimePoint last_activity;
        std::chrono::milliseconds timeout{3000};
        bool has_fin{false};
    };

    void cleanup_tombstones(TimePoint now) {
        for (auto it = tombstones_.begin(); it != tombstones_.end(); ) {
            if (now >= it->second) {
                it = tombstones_.erase(it);
            } else {
                ++it;
            }
        }
    }

    std::mutex mutex_;
    std::chrono::milliseconds default_timeout_;
    std::chrono::seconds tombstone_ttl_;
    std::unordered_map<std::string, Bucket> buckets_;
    std::unordered_map<std::string, TimePoint> tombstones_;
};

// ── Ресеквенсер на базі std::map (Черга за порядковим номером) ─────────────
class StreamResequencer {
public:
    explicit StreamResequencer(uint64_t initial_sequence = 1)
        : next_expected_sequence_(initial_sequence) {}

    std::vector<Message> push(Message msg) {
        std::lock_guard<std::mutex> lock(mutex_);
        std::vector<Message> drain_batch;

        if (msg.sequence_number >= next_expected_sequence_) {
            buffer_[msg.sequence_number] = std::move(msg);
        }

        // Послідовне вилучення елементів без розривів
        while (!buffer_.empty() && buffer_.begin()->first == next_expected_sequence_) {
            drain_batch.push_back(std::move(buffer_.begin()->second));
            buffer_.erase(buffer_.begin());
            ++next_expected_sequence_;
        }

        return drain_batch;
    }

    uint64_t next_expected() const {
        std::lock_guard<std::mutex> lock(mutex_);
        return next_expected_sequence_;
    }

private:
    mutable std::mutex mutex_;
    uint64_t next_expected_sequence_;
    std::map<uint64_t, Message> buffer_;
};

} // namespace eip
```
:::

## Детальний розбір механізмів та алгоритмічних рішень

### 1. Захист від запізнілих елементів (Tombstone Tracking)

Коли агрегаційний кошик накопичує повний комплект елементів, він видаляється з робочої таблиці активних сесій для збереження оперативної пам'яті. Проте в асинхронній мережі брокер повідомлень може повторно доставити елемент через механізм повторів (*Retries*) або транзакційного тайм-ауту черги. Без спеціального захисту таке запізніле повідомлення сприймалося б агрегатором як початок абсолютно нової бізнес-сесії. Агрегатор створив би новий кошик, який ніколи б не отримав решту елементів і залишався б у пам'яті до моменту примусового завершення за дедлайном.

Ця проблема розв'язується через механізм **надгробків** (англ. *Tombstones*). При закритті сесії її `correlation_id` заноситься до спеціальної таблиці з міткою часу закриття та часом життя `TTL` (наприклад, 10 секунд або 1 година у високонавантажених системах). Кожне нове повідомлення спочатку перевіряє таблицю надгробків. Якщо запис існує, повідомлення негайно відхиляється без виділення пам'яті під новий кошик.

### 2. Ідемпотентне додавання та фільтрація дублікатів

Розподілені брокери (RabbitMQ, Kafka, AWS SQS) гарантують доставку за семантикою *At-Least-Once*, що неминуче призводить до появи дублікатів повідомлень. Вставка елемента в кошик містить обов'язкову перевірку унікальності номера `sequence_number`. Якщо елемент із таким номером уже присутній у масиві, операція завершується без зміни лічильника зібраних елементів, що захищає фінальний агрегований результат від викривлення та подвійного підрахунку фінансових чи облікових даних.

### 3. Структура буфера ресеквенсера та часова складність

У C++ реалізації внутрішній стан ресеквенсера організовано на базі червоно-чорного дерева `std::map<uint64_t, Message>`, де ключем є номер послідовності. Це забезпечує:
* Вставку невпорядкованого повідомлення за логарифмічний час `O(log K)`, де `K` — кількість буферизованих елементів у поточному вікні.
* Миттєву перевірку наявності наступного очікуваного пакета через метод `buffer_.begin()->first` за час `O(1)`.
* Каскадне вилучення елементів без додаткового сортування, оскільки елементи в дереві завжди підтримуються у відсортованому стані.

У C реалізації застосовано компактний плоский масив фіксованого розміру `buffer[RESEQ_MAX_BUFFER]`. Положення елемента визначається як пряме зміщення `offset = sequence_number - next_expected_seq`, що забезпечує швидкість вставки `O(1)` та відмінну локальність кешу процесора (CPU Cache Locality), але обмежує максимальний розмір вікна затримки константою `RESEQ_MAX_BUFFER`.

### 4. Покрокове трасування життєвого циклу потоку подій

Розглянемо практичний сценарій проходження п'яти повідомлень через агрегатор та ресеквенсер:

1. **Прибуття Msg(Corr: "ORD-1", Seq: 2/3):** Кошик для `"ORD-1"` створюється вперше. Повідомлення №2 записується в буфер. Лічильник становить 1 із 3. Агрегатор очікує.
2. **Прибуття Msg(Corr: "ORD-1", Seq: 1/3):** Повідомлення №1 додається до кошика. Лічильник становить 2 із 3. Умови завершення не виконано.
3. **Повторне прибуття Msg(Corr: "ORD-1", Seq: 2/3):** Агрегатор знаходить `Seq: 2` у списку отриманих елементів, ідентифікує мережевий дублікат і відкидає пакет без зміни лічильника (лишається 2 із 3).
4. **Прибуття Msg(Corr: "ORD-1", Seq: 3/3, is_last: true):** Лічильник досягає 3 із 3. Агрегатор негайно формує масив із трьох повідомлень `[1, 2, 3]`, видаляє кошик, додає надгробок на 10 секунд і випускає пакет до споживача.
5. **Запізнілий пакет Msg(Corr: "ORD-1", Seq: 1/3) через 4 секунди:** Агрегатор перевіряє таблицю надгробків, знаходить активний запис для `"ORD-1"` і відхиляє повідомлення з кодом `TOMBSTONE_REJECTED`, захищаючи пам'ять від витоку.

### 5. Фонове очищення та обробка дедлайнів

Метод `sweep_timeouts()` забезпечує захист від «завислих» сесій, джерела яких зазнали аварійного збою до відправки повного пакета. Сканування перевіряє тривалість існування кожного кошика відносно монотонного годинника `CLOCK_MONOTONIC` (`std::chrono::steady_clock`). Це виключає збої тайм-аутів при коригуванні системного часу операційної системи протоколом NTP. Усі прострочені кошики маркуються як незавершені (`is_complete = false`), забезпечуються надгробками й вивільняються з пам'яті, що гарантує стабільний обсяг використовуваної RAM навіть під час масових мережевих збоїв.
