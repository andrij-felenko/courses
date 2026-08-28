#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define REORDER_BUF_CAPACITY 64
#define REORDER_MAX_PAYLOAD  256

typedef struct {
    uint32_t seq;
    uint32_t timestamp_ms;
    uint16_t len;
    uint8_t  data[REORDER_MAX_PAYLOAD];
    bool     occupied;
} packet_slot_t;

typedef struct {
    packet_slot_t slots[REORDER_BUF_CAPACITY];
    uint32_t seq_expected;
    uint32_t gap_start_time_ms;
    uint32_t gap_timeout_ms;
    bool     is_initialized;
} reorder_buffer_t;

void reorder_buf_init(reorder_buffer_t *rb, uint32_t timeout_ms) {
    memset(rb, 0, sizeof(*rb));
    rb->gap_timeout_ms = timeout_ms;
    rb->is_initialized = false;
}

/* Вставка пакета в буфер. Повертає true, якщо пакет прийнято до черги */
bool reorder_buf_push(reorder_buffer_t *rb, uint32_t seq, const uint8_t *payload,
                      uint16_t len, uint32_t now_ms) {
    if (len > REORDER_MAX_PAYLOAD) {
        return false;
    }

    if (!rb->is_initialized) {
        rb->seq_expected = seq;
        rb->is_initialized = true;
    }

    int32_t diff = (int32_t)(seq - rb->seq_expected);

    /* Застарілий номер або дублікат */
    if (diff < 0) {
        return false;
    }

    /* Переповнення місткості буфера */
    if (diff >= REORDER_BUF_CAPACITY) {
        return false;
    }

    uint32_t idx = seq % REORDER_BUF_CAPACITY;
    packet_slot_t *slot = &rb->slots[idx];

    /* Пакет уже є в слоті (дублікат) */
    if (slot->occupied && slot->seq == seq) {
        return false;
    }

    slot->seq = seq;
    slot->len = len;
    slot->timestamp_ms = now_ms;
    memcpy(slot->data, payload, len);
    slot->occupied = true;

    return true;
}

/* Витягнення наступного суцільного пакета за чергою.
   Повертає довжину скопійованих даних або 0, якщо черга вперлася в дірку/порожня */
uint16_t reorder_buf_pop(reorder_buffer_t *rb, uint8_t *out_buf, uint32_t *out_seq) {
    if (!rb->is_initialized) {
        return 0;
    }

    uint32_t idx = rb->seq_expected % REORDER_BUF_CAPACITY;
    packet_slot_t *slot = &rb->slots[idx];

    if (slot->occupied && slot->seq == rb->seq_expected) {
        uint16_t len = slot->len;
        memcpy(out_buf, slot->data, len);
        if (out_seq) {
            *out_seq = slot->seq;
        }

        /* Звільняємо слот і просуваємо очікування */
        slot->occupied = false;
        rb->seq_expected++;
        rb->gap_start_time_ms = 0; /* Скидаємо таймер дірки */
        return len;
    }

    return 0; /* Очікуємо приходу rb->seq_expected */
}

/* Обробка таймауту очікування дірки */
void reorder_buf_tick(reorder_buffer_t *rb, uint32_t now_ms) {
    if (!rb->is_initialized) {
        return;
    }

    uint32_t idx = rb->seq_expected % REORDER_BUF_CAPACITY;
    if (rb->slots[idx].occupied) {
        return; /* Слот заповнений, таймаут не потрібен */
    }

    /* Перевіряємо, чи є взагалі якісь пізніші пакети в буфері */
    bool has_future_packets = false;
    for (int i = 0; i < REORDER_BUF_CAPACITY; ++i) {
        if (rb->slots[i].occupied) {
            has_future_packets = true;
            break;
        }
    }

    if (!has_future_packets) {
        rb->gap_start_time_ms = 0;
        return;
    }

    if (rb->gap_start_time_ms == 0) {
        rb->gap_start_time_ms = now_ms;
    } else if (now_ms - rb->gap_start_time_ms >= rb->gap_timeout_ms) {
        /* Таймаут сплив: пропускаємо втрачений пакет seq_expected */
        rb->seq_expected++;
        rb->gap_start_time_ms = 0;
    }
}
