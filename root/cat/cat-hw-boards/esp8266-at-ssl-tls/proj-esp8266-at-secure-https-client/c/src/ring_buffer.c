#include "ring_buffer.h"
#include <string.h>

bool ring_buffer_init(ring_buffer_t *rb, uint8_t *storage, size_t capacity) {
    if (!rb || !storage || capacity == 0) {
        return false;
    }
    rb->buffer = storage;
    rb->capacity = capacity;
    rb->head = 0;
    rb->tail = 0;

    /* Перевіряємо, чи є capacity ступенем двійки для прискорення обчислень індексів через маску */
    if ((capacity & (capacity - 1)) == 0) {
        rb->mask = capacity - 1;
    } else {
        rb->mask = 0;
    }
    return true;
}

bool ring_buffer_push(ring_buffer_t *rb, uint8_t byte) {
    if (!rb || !rb->buffer) {
        return false;
    }

    size_t current_head = rb->head;
    size_t current_tail = rb->tail;
    size_t next_head;

    if (rb->mask != 0) {
        next_head = (current_head + 1) & rb->mask;
    } else {
        next_head = (current_head + 1) % rb->capacity;
    }

    /* Якщо наступний head дорівнює tail — буфер повністю заповнений */
    if (next_head == current_tail) {
        return false;
    }

    rb->buffer[current_head] = byte;
    rb->head = next_head;
    return true;
}

size_t ring_buffer_push_bytes(ring_buffer_t *rb, const uint8_t *data, size_t len) {
    if (!rb || !data) {
        return 0;
    }

    size_t written = 0;
    for (size_t i = 0; i < len; ++i) {
        if (!ring_buffer_push(rb, data[i])) {
            break;
        }
        written++;
    }
    return written;
}

bool ring_buffer_pop(ring_buffer_t *rb, uint8_t *byte) {
    if (!rb || !rb->buffer || !byte) {
        return false;
    }

    size_t current_tail = rb->tail;
    size_t current_head = rb->head;

    if (current_tail == current_head) {
        return false; /* Буфер порожній */
    }

    *byte = rb->buffer[current_tail];
    if (rb->mask != 0) {
        rb->tail = (current_tail + 1) & rb->mask;
    } else {
        rb->tail = (current_tail + 1) % rb->capacity;
    }
    return true;
}

size_t ring_buffer_pop_bytes(ring_buffer_t *rb, uint8_t *dest, size_t max_len) {
    if (!rb || !dest) {
        return 0;
    }

    size_t read_bytes = 0;
    while (read_bytes < max_len) {
        uint8_t byte;
        if (!ring_buffer_pop(rb, &byte)) {
            break;
        }
        dest[read_bytes++] = byte;
    }
    return read_bytes;
}

bool ring_buffer_peek(const ring_buffer_t *rb, size_t offset, uint8_t *byte) {
    if (!rb || !rb->buffer || !byte) {
        return false;
    }

    size_t avail = ring_buffer_available(rb);
    if (offset >= avail) {
        return false;
    }

    size_t idx;
    if (rb->mask != 0) {
        idx = (rb->tail + offset) & rb->mask;
    } else {
        idx = (rb->tail + offset) % rb->capacity;
    }

    *byte = rb->buffer[idx];
    return true;
}

size_t ring_buffer_available(const ring_buffer_t *rb) {
    if (!rb) {
        return 0;
    }

    size_t current_head = rb->head;
    size_t current_tail = rb->tail;

    if (current_head >= current_tail) {
        return current_head - current_tail;
    } else {
        return rb->capacity - current_tail + current_head;
    }
}

size_t ring_buffer_free_space(const ring_buffer_t *rb) {
    if (!rb) {
        return 0;
    }
    return rb->capacity - 1 - ring_buffer_available(rb);
}

size_t ring_buffer_skip(ring_buffer_t *rb, size_t len) {
    if (!rb) {
        return 0;
    }

    size_t avail = ring_buffer_available(rb);
    size_t to_skip = (len < avail) ? len : avail;

    if (rb->mask != 0) {
        rb->tail = (rb->tail + to_skip) & rb->mask;
    } else {
        rb->tail = (rb->tail + to_skip) % rb->capacity;
    }
    return to_skip;
}

void ring_buffer_clear(ring_buffer_t *rb) {
    if (!rb) {
        return;
    }
    rb->head = 0;
    rb->tail = 0;
}

int ring_buffer_find_pattern(const ring_buffer_t *rb, const char *pattern) {
    if (!rb || !pattern) {
        return -1;
    }

    size_t pat_len = strlen(pattern);
    size_t avail = ring_buffer_available(rb);

    if (pat_len == 0 || avail < pat_len) {
        return -1;
    }

    size_t max_search = avail - pat_len;
    for (size_t i = 0; i <= max_search; ++i) {
        bool match = true;
        for (size_t j = 0; j < pat_len; ++j) {
            uint8_t byte;
            if (!ring_buffer_peek(rb, i + j, &byte) || (char)byte != pattern[j]) {
                match = false;
                break;
            }
        }
        if (match) {
            return (int)i;
        }
    }
    return -1;
}
