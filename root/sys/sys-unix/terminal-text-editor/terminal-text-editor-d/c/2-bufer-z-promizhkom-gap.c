#include <stdlib.h>
#include <string.h>

struct GapBuffer {
    char *buffer;
    size_t capacity;
    size_t gap_start;
    size_t gap_end;
};

void gap_init(struct GapBuffer *gb, size_t initial_cap) {
    gb->capacity = initial_cap ? initial_cap : 64;
    gb->buffer = malloc(gb->capacity);
    gb->gap_start = 0;
    gb->gap_end = gb->capacity;
}

void gap_insert_char(struct GapBuffer *gb, char c) {
    if (gb->gap_start == gb->gap_end) {
        // Розширення проміжку при вичерпанні вільного місця
        size_t new_cap = gb->capacity * 2;
        char *new_buf = malloc(new_cap);
        size_t post_gap_len = gb->capacity - gb->gap_end;
        size_t new_gap_end = new_cap - post_gap_len;

        memcpy(new_buf, gb->buffer, gb->gap_start);
        memcpy(new_buf + new_gap_end, gb->buffer + gb->gap_end, post_gap_len);

        free(gb->buffer);
        gb->buffer = new_buf;
        gb->gap_end = new_gap_end;
        gb->capacity = new_cap;
    }
    gb->buffer[gb->gap_start++] = c;
}

void gap_move_cursor(struct GapBuffer *gb, size_t new_pos) {
    if (new_pos < gb->gap_start) {
        size_t delta = gb->gap_start - new_pos;
        memmove(gb->buffer + gb->gap_end - delta, gb->buffer + new_pos, delta);
        gb->gap_start -= delta;
        gb->gap_end -= delta;
    } else if (new_pos > gb->gap_start) {
        size_t delta = new_pos - gb->gap_start;
        memmove(gb->buffer + gb->gap_start, gb->buffer + gb->gap_end, delta);
        gb->gap_start += delta;
        gb->gap_end += delta;
    }
}
