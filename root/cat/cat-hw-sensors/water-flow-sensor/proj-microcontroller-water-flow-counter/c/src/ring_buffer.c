#include "ring_buffer.h"

void ring_buffer_init(ring_buffer_t *rb) {
    if (rb == NULL) {
        return;
    }
    rb->head = 0;
    rb->tail = 0;
    rb->overflow_count = 0;
}

bool ring_buffer_push(ring_buffer_t *rb, ring_buffer_element_t element) {
    if (rb == NULL) {
        return false;
    }

    uint16_t next_head = (rb->head + 1U) & (RING_BUFFER_CAPACITY - 1U);

    /* Перевірка на переповнення буфера */
    if (next_head == rb->tail) {
        rb->overflow_count++;
        return false;
    }

    rb->data[rb->head] = element;
    rb->head = next_head;
    return true;
}

bool ring_buffer_pop(ring_buffer_t *rb, ring_buffer_element_t *element) {
    if (rb == NULL || element == NULL) {
        return false;
    }

    if (rb->head == rb->tail) {
        return false; /* Буфер порожній */
    }

    *element = rb->data[rb->tail];
    rb->tail = (rb->tail + 1U) & (RING_BUFFER_CAPACITY - 1U);
    return true;
}

bool ring_buffer_is_empty(const ring_buffer_t *rb) {
    if (rb == NULL) {
        return true;
    }
    return (rb->head == rb->tail);
}

bool ring_buffer_is_full(const ring_buffer_t *rb) {
    if (rb == NULL) {
        return false;
    }
    uint16_t next_head = (rb->head + 1U) & (RING_BUFFER_CAPACITY - 1U);
    return (next_head == rb->tail);
}

uint16_t ring_buffer_count(const ring_buffer_t *rb) {
    if (rb == NULL) {
        return 0;
    }
    return (rb->head - rb->tail) & (RING_BUFFER_CAPACITY - 1U);
}

float ring_buffer_calculate_average_frequency(ring_buffer_t *rb, uint32_t window_us) {
    if (rb == NULL || window_us == 0 || ring_buffer_is_empty(rb)) {
        return 0.0f;
    }

    uint32_t total_pulses = 0;
    uint32_t min_timestamp = 0xFFFFFFFFU;
    uint32_t max_timestamp = 0U;
    uint16_t count = 0;

    uint16_t current_tail = rb->tail;
    uint16_t current_head = rb->head;

    while (current_tail != current_head) {
        ring_buffer_element_t elem = rb->data[current_tail];
        total_pulses += elem.pulse_increment;
        
        if (elem.timestamp_us < min_timestamp) {
            min_timestamp = elem.timestamp_us;
        }
        if (elem.timestamp_us > max_timestamp) {
            max_timestamp = elem.timestamp_us;
        }
        count++;

        current_tail = (current_tail + 1U) & (RING_BUFFER_CAPACITY - 1U);
    }

    if (count == 0 || max_timestamp <= min_timestamp) {
        return 0.0f;
    }

    uint32_t dt_us = max_timestamp - min_timestamp;
    if (dt_us == 0) {
        return 0.0f;
    }

    /* Обчислення частоти: f = (імпульси - 1) / dt_sec */
    float dt_sec = (float)dt_us / 1000000.0f;
    if (total_pulses > 1) {
        return ((float)(total_pulses - 1)) / dt_sec;
    }

    return (float)total_pulses / dt_sec;
}
