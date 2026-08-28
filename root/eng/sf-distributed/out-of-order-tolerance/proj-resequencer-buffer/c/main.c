#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>

#define RESEQUENCER_CAPACITY 256

typedef struct {
    uint64_t seq;
    char payload[128];
    bool occupied;
    uint64_t arrival_time_ms;
} ResequencerSlot;

typedef void (*DeliverCallback)(uint64_t seq, const char* payload, void* user_data);
typedef void (*GapDropCallback)(uint64_t lost_seq, void* user_data);

typedef struct {
    uint64_t expected_seq;
    uint64_t gap_timeout_ms;
    uint64_t gap_detected_at_ms;
    bool has_active_gap;
    ResequencerSlot buffer[RESEQUENCER_CAPACITY];
    DeliverCallback on_deliver;
    GapDropCallback on_gap_drop;
    void* user_data;
} Resequencer;

static uint64_t get_current_time_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000ULL + (uint64_t)ts.tv_nsec / 1000000ULL;
}

void resequencer_init(Resequencer* r, uint64_t start_seq, uint64_t gap_timeout_ms,
                      DeliverCallback deliver_cb, GapDropCallback drop_cb, void* user_data) {
    r->expected_seq = start_seq;
    r->gap_timeout_ms = gap_timeout_ms;
    r->gap_detected_at_ms = 0;
    r->has_active_gap = false;
    r->on_deliver = deliver_cb;
    r->on_gap_drop = drop_cb;
    r->user_data = user_data;
    for (size_t i = 0; i < RESEQUENCER_CAPACITY; ++i) {
        r->buffer[i].occupied = false;
    }
}

static void flush_continuous_prefix(Resequencer* r) {
    while (true) {
        size_t slot_idx = r->expected_seq % RESEQUENCER_CAPACITY;
        ResequencerSlot* slot = &r->buffer[slot_idx];

        if (!slot->occupied || slot->seq != r->expected_seq) {
            break; // Знайдено прогалину
        }

        // Передаємо впорядковане повідомлення прикладному обробнику
        r->on_deliver(slot->seq, slot->payload, r->user_data);
        slot->occupied = false;
        r->expected_seq++;
    }

    // Перевіряємо, чи лишилися в буфері майбутні повідомлення
    bool has_pending = false;
    for (size_t i = 0; i < RESEQUENCER_CAPACITY; ++i) {
        if (r->buffer[i].occupied) {
            has_pending = true;
            break;
        }
    }

    if (has_pending) {
        if (!r->has_active_gap) {
            r->has_active_gap = true;
            r->gap_detected_at_ms = get_current_time_ms();
        }
    } else {
        r->has_active_gap = false;
    }
}

bool resequencer_push(Resequencer* r, uint64_t seq, const char* payload) {
    uint64_t now = get_current_time_ms();

    // 1. Відкидаємо застарілі дублікати
    if (seq < r->expected_seq) {
        return false;
    }

    // 2. Якщо повідомлення прибуло точно вчасно
    if (seq == r->expected_seq) {
        r->on_deliver(seq, payload, r->user_data);
        r->expected_seq++;
        flush_continuous_prefix(r);
        return true;
    }

    // 3. Позачергове майбутнє повідомлення — перевірка меж вікна
    if (seq >= r->expected_seq + RESEQUENCER_CAPACITY) {
        // Повідомлення виходить за межі буфера (Window Overflow)
        return false;
    }

    size_t slot_idx = seq % RESEQUENCER_CAPACITY;
    ResequencerSlot* slot = &r->buffer[slot_idx];

    if (slot->occupied && slot->seq == seq) {
        return false; // Повторний дублікат у буфері
    }

    slot->seq = seq;
    strncpy(slot->payload, payload, sizeof(slot->payload) - 1);
    slot->payload[sizeof(slot->payload) - 1] = '\0';
    slot->occupied = true;
    slot->arrival_time_ms = now;

    if (!r->has_active_gap) {
        r->has_active_gap = true;
        r->gap_detected_at_ms = now;
    }

    return true;
}

void resequencer_tick(Resequencer* r) {
    if (!r->has_active_gap) {
        return;
    }

    uint64_t now = get_current_time_ms();
    if (now - r->gap_detected_at_ms >= r->gap_timeout_ms) {
        // Таймаут вичерпано: фіксуємо втрату очікуваного повідомлення
        r->on_gap_drop(r->expected_seq, r->user_data);
        r->expected_seq++; // Примусово пропускаємо прогалину
        r->has_active_gap = false;

        // Просуваємо буфер далі
        flush_continuous_prefix(r);
    }
}
