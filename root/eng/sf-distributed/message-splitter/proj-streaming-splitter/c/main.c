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
