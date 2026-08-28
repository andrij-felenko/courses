/* trace_logger.h — Реалізація неблокуючого логера трафіку мовою C */
#ifndef TRACE_LOGGER_H
#define TRACE_LOGGER_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define TRACE_PKT_MAX_LEN   128
#define TRACE_QUEUE_SLOTS    16

typedef enum {
    TRACE_DIR_RX = 0x01,
    TRACE_DIR_TX = 0x02
} trace_direction_t;

typedef struct {
    uint32_t timestamp_us;
    trace_direction_t direction;
    uint16_t length;
    uint8_t payload[TRACE_PKT_MAX_LEN];
} trace_record_t;

typedef struct {
    trace_record_t records[TRACE_QUEUE_SLOTS];
    volatile uint32_t head;
    volatile uint32_t tail;
    volatile uint32_t dropped_count;
} trace_queue_t;

void trace_queue_init(trace_queue_t *q);
bool trace_queue_push(trace_queue_t *q, trace_direction_t dir, uint32_t time_us,
                      const uint8_t *data, uint16_t len);
bool trace_queue_pop(trace_queue_t *q, trace_record_t *out_record);
size_t trace_format_hex(const trace_record_t *rec, char *out_buf, size_t max_out);

#endif /* TRACE_LOGGER_H */

/* trace_logger.c */
#include "trace_logger.h"
#include <string.h>
#include <stdio.h>

void trace_queue_init(trace_queue_t *q) {
    q->head = 0;
    q->tail = 0;
    q->dropped_count = 0;
}

bool trace_queue_push(trace_queue_t *q, trace_direction_t dir, uint32_t time_us,
                      const uint8_t *data, uint16_t len) {
    uint32_t next_head = (q->head + 1) % TRACE_QUEUE_SLOTS;
    if (next_head == q->tail) {
        q->dropped_count++;
        return false; /* Черга переповнена — фіксуємо втрату */
    }

    trace_record_t *slot = &q->records[q->head];
    slot->timestamp_us = time_us;
    slot->direction = dir;

    uint16_t copy_len = (len > TRACE_PKT_MAX_LEN) ? TRACE_PKT_MAX_LEN : len;
    slot->length = copy_len;
    memcpy(slot->payload, data, copy_len);

    q->head = next_head;
    return true;
}

bool trace_queue_pop(trace_queue_t *q, trace_record_t *out_record) {
    if (q->head == q->tail) {
        return false; /* Черга порожня */
    }

    *out_record = q->records[q->tail];
    q->tail = (q->tail + 1) % TRACE_QUEUE_SLOTS;
    return true;
}

size_t trace_format_hex(const trace_record_t *rec, char *out_buf, size_t max_out) {
    if (max_out < 64) return 0;

    uint32_t sec = rec->timestamp_us / 1000000;
    uint32_t us  = rec->timestamp_us % 1000000;
    const char *dir_str = (rec->direction == TRACE_DIR_RX) ? "RX" : "TX";

    int written = snprintf(out_buf, max_out, "[%04lu.%06lu] [%s] ",
                           (unsigned long)sec, (unsigned long)us, dir_str);
    if (written < 0 || (size_t)written >= max_out) return 0;

    size_t offset = (size_t)written;
    for (uint16_t i = 0; i < rec->length && (offset + 4) < max_out; i++) {
        written = snprintf(&out_buf[offset], max_out - offset, "%02X ", rec->payload[i]);
        if (written > 0) offset += (size_t)written;
    }

    if (offset < max_out) {
        out_buf[offset++] = '\n';
        out_buf[offset] = '\0';
    }
    return offset;
}
