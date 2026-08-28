#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define BUFFER_SLOTS      64
#define MAX_PAYLOAD_SIZE  160  /* 20 мс G.711 аудіо при 8 кГц */
#define CLOCK_RATE_HZ     8000
#define PACKET_TIME_MS    20
#define SAMPLES_PER_FRAME (CLOCK_RATE_HZ * PACKET_TIME_MS / 1000)

typedef struct {
    uint16_t seq_num;
    uint32_t timestamp;
    uint32_t arrival_time_ms;
    uint8_t  payload[MAX_PAYLOAD_SIZE];
    size_t   payload_len;
    bool     occupied;
} PacketSlot;

typedef struct {
    PacketSlot slots[BUFFER_SLOTS];
    uint16_t   next_play_seq;
    uint32_t   target_delay_ms;
    uint32_t   min_transit_ms;
    int32_t    jitter_q4;        /* Джитер у форматі Q4 (фіксована кома * 16) */
    uint32_t   last_transit_ms;
    bool       initialized;
    
    /* Статистика */
    uint32_t   packets_received;
    uint32_t   packets_played;
    uint32_t   packets_late_dropped;
    uint32_t   packets_underrun;
} JitterBuffer;

void jb_init(JitterBuffer *jb, uint32_t initial_target_delay_ms) {
    memset(jb, 0, sizeof(JitterBuffer));
    jb->target_delay_ms = initial_target_delay_ms;
    jb->min_transit_ms = UINT32_MAX;
}

/* Порівняння 16-бітних номерів послідовності з урахуванням переповнення */
static inline bool seq_less(uint16_t s1, uint16_t s2) {
    return (int16_t)(s1 - s2) < 0;
}

void jb_put_packet(JitterBuffer *jb, uint16_t seq, uint32_t timestamp,
                   const uint8_t *payload, size_t len, uint32_t arrival_ms) {
    jb->packets_received++;

    if (!jb->initialized) {
        jb->next_play_seq = seq;
        jb->initialized = true;
    }

    /* Відкидаємо пакети, чий дедлайн відтворення вже минув */
    if (seq_less(seq, jb->next_play_seq)) {
        jb->packets_late_dropped++;
        return;
    }

    /* Оцінка транзитної затримки та джитеру (RFC 3550 EWMA) */
    uint32_t transit_ms = arrival_ms - (timestamp / (CLOCK_RATE_HZ / 1000));
    if (transit_ms < jb->min_transit_ms) {
        jb->min_transit_ms = transit_ms;
    }

    if (jb->packets_received > 1) {
        int32_t diff_ms = (int32_t)transit_ms - (int32_t)jb->last_transit_ms;
        if (diff_ms < 0) diff_ms = -diff_ms;
        
        /* J_i = J_{i-1} + (|D| - J_{i-1}) / 16 */
        jb->jitter_q4 += diff_ms - (jb->jitter_q4 >> 4);
    }
    jb->last_transit_ms = transit_ms;

    /* Адаптація цільової затримки: Target = MinDelay + 3 * Jitter */
    uint32_t current_jitter_ms = (uint32_t)(jb->jitter_q4 >> 4);
    uint32_t calculated_target = current_jitter_ms * 3 + 20;
    if (calculated_target < 20) calculated_target = 20;
    if (calculated_target > 200) calculated_target = 200;
    jb->target_delay_ms = calculated_target;

    /* Збереження пакета в кільцевий слот */
    size_t idx = seq % BUFFER_SLOTS;
    PacketSlot *slot = &jb->slots[idx];
    slot->seq_num = seq;
    slot->timestamp = timestamp;
    slot->arrival_time_ms = arrival_ms;
    slot->payload_len = (len > MAX_PAYLOAD_SIZE) ? MAX_PAYLOAD_SIZE : len;
    memcpy(slot->payload, payload, slot->payload_len);
    slot->occupied = true;
}

/* Вичитування аудіокадру для відтворення (викликається кожні 20 мс) */
bool jb_get_frame(JitterBuffer *jb, uint8_t *out_frame, size_t *out_len) {
    if (!jb->initialized) {
        return false;
    }

    size_t idx = jb->next_play_seq % BUFFER_SLOTS;
    PacketSlot *slot = &jb->slots[idx];

    if (slot->occupied && slot->seq_num == jb->next_play_seq) {
        memcpy(out_frame, slot->payload, slot->payload_len);
        *out_len = slot->payload_len;
        slot->occupied = false;
        jb->next_play_seq++;
        jb->packets_played++;
        return true;
    }

    /* Буферне виснаження: потрібний пакет ще не дійшов */
    jb->packets_underrun++;
    jb->next_play_seq++; /* Пропускаємо дедлайн, передаємо керування PLC */
    return false;
}
