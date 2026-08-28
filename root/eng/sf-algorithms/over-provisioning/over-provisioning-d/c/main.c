#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

typedef struct {
    int *data;
    size_t size;
    size_t capacity;
    size_t realloc_count;
} DynamicBufferC;

DynamicBufferC* buffer_create(size_t initial_cap) {
    DynamicBufferC *buf = (DynamicBufferC*)malloc(sizeof(DynamicBufferC));
    if (!buf) return NULL;

    buf->size = 0;
    buf->capacity = initial_cap > 0 ? initial_cap : 4;
    buf->realloc_count = 0;
    buf->data = (int*)malloc(buf->capacity * sizeof(int));
    if (!buf->data) {
        free(buf);
        return NULL;
    }
    return buf;
}

bool buffer_push(DynamicBufferC *buf, int value) {
    // 1. Розширення при 100% заповненні (Over-provisioning x1.5)
    if (buf->size == buf->capacity) {
        size_t new_cap = buf->capacity + (buf->capacity >> 1); // x1.5
        int *new_data = (int*)realloc(buf->data, new_cap * sizeof(int));
        if (!new_data) return false;

        buf->data = new_data;
        buf->capacity = new_cap;
        buf->realloc_count++;
    }
    buf->data[buf->size++] = value;
    return true;
}

bool buffer_pop(DynamicBufferC *buf, int *out_val) {
    if (buf->size == 0) return false;

    buf->size--;
    if (out_val) *out_val = buf->data[buf->size];

    // 2. Гістерезисне стиснення лише при падінні заповненості нижче 25%
    if (buf->size > 0 && buf->size <= buf->capacity / 4 && buf->capacity > 16) {
        size_t new_cap = buf->capacity / 2;
        int *new_data = (int*)realloc(buf->data, new_cap * sizeof(int));
        if (new_data) {
            buf->data = new_data;
            buf->capacity = new_cap;
            buf->realloc_count++;
        }
    }
    return true;
}

void buffer_free(DynamicBufferC *buf) {
    if (buf) {
        free(buf->data);
        free(buf);
    }
}
