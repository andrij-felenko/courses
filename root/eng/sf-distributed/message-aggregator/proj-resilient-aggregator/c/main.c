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
