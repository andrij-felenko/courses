#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>

#define ARQ_MAX_RETRIES     3
#define ARQ_TIMEOUT_MS      800

typedef struct {
    uint16_t expected_sequence;
    bool     is_initialized;
    bool     gap_active;
    uint16_t gap_first_seq;
    uint16_t gap_last_seq;
    uint32_t last_request_time_ms;
    uint8_t  retry_count;
} event_gap_tracker_t;

void gap_tracker_init(event_gap_tracker_t *tracker) {
    memset(tracker, 0, sizeof(event_gap_tracker_t));
}

// Обробка номера послідовності з вхідного EVENT або CURRENT_EVENT_SEQUENCE
void gap_tracker_on_sequence(event_gap_tracker_t *tracker,
                             uint16_t received_seq,
                             uint32_t current_time_ms,
                             uint8_t sys_id,
                             uint8_t comp_id) {
    if (!tracker->is_initialized) {
        tracker->expected_sequence = (uint16_t)((received_seq + 1) & 0xFFFF);
        tracker->is_initialized = true;
        return;
    }

    if (received_seq == tracker->expected_sequence) {
        tracker->expected_sequence = (uint16_t)((tracker->expected_sequence + 1) & 0xFFFF);
        if (tracker->gap_active && tracker->expected_sequence > tracker->gap_last_seq) {
            tracker->gap_active = false;
            tracker->retry_count = 0;
        }
    } else {
        uint16_t diff = (uint16_t)(received_seq - tracker->expected_sequence);
        if (diff < 32768) {
            tracker->gap_active = true;
            tracker->gap_first_seq = tracker->expected_sequence;
            tracker->gap_last_seq = (uint16_t)((received_seq - 1) & 0xFFFF);
            tracker->last_request_time_ms = current_time_ms;
            tracker->retry_count = 1;

            printf("[ARQ] Gap detected: missing %u..%u. Sending REQUEST_EVENT (sys=%u comp=%u)\n",
                   tracker->gap_first_seq, tracker->gap_last_seq, sys_id, comp_id);
        }
    }
}

// Періодичне оновлення стану та повтор запитів за тайм-аутом
void gap_tracker_poll(event_gap_tracker_t *tracker,
                      uint32_t current_time_ms,
                      uint8_t sys_id,
                      uint8_t comp_id) {
    if (!tracker->gap_active) {
        return;
    }

    if (current_time_ms - tracker->last_request_time_ms >= ARQ_TIMEOUT_MS) {
        if (tracker->retry_count < ARQ_MAX_RETRIES) {
            tracker->retry_count++;
            tracker->last_request_time_ms = current_time_ms;
            printf("[ARQ] Retry %u/%u for missing %u..%u\n",
                   tracker->retry_count, ARQ_MAX_RETRIES,
                   tracker->gap_first_seq, tracker->gap_last_seq);
        } else {
            printf("[ARQ] Gap %u..%u permanently lost after %u retries.\n",
                   tracker->gap_first_seq, tracker->gap_last_seq, ARQ_MAX_RETRIES);
            tracker->expected_sequence = (uint16_t)((tracker->gap_last_seq + 1) & 0xFFFF);
            tracker->gap_active = false;
            tracker->retry_count = 0;
        }
    }
}
