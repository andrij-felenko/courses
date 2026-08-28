#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

/* Простий лінійний арена-алокатор для швидкого створення Sparse Table */
typedef struct {
    uint8_t *buffer;
    size_t capacity;
    size_t offset;
} arena_allocator_t;

void *arena_alloc(arena_allocator_t *arena, size_t size, size_t align) {
    size_t current_addr = (size_t)(arena->buffer + arena->offset);
    size_t aligned_addr = (current_addr + align - 1) & ~(align - 1);
    size_t new_offset = (aligned_addr - (size_t)arena->buffer) + size;

    if (new_offset > arena->capacity) return NULL; /* Переповнення арени */

    arena->offset = new_offset;
    return (void *)aligned_addr;
}

sparse_table_t *st_create_arena(arena_allocator_t *arena, const int32_t *arr, size_t n) {
    if (!arena || !arr || n == 0) return NULL;

    sparse_table_t *st = (sparse_table_t *)arena_alloc(arena, sizeof(sparse_table_t), sizeof(void*));
    if (!st) return NULL;

    st->n = n;
    st->levels = (size_t)(31 - __builtin_clz((uint32_t)n)) + 1;
    st->data = (int32_t *)arena_alloc(arena, st->levels * n * sizeof(int32_t), sizeof(int32_t));
    if (!st->data) return NULL;

    for (size_t i = 0; i < n; ++i) st->data[i] = arr[i];

    for (size_t j = 1; j < st->levels; ++j) {
        size_t half = 1 << (j - 1);
        size_t row_curr = j * n;
        size_t row_prev = (j - 1) * n;
        for (size_t i = 0; i + (1 << j) <= n; ++i) {
            int32_t a = st->data[row_prev + i];
            int32_t b = st->data[row_prev + i + half];
            st->data[row_curr + i] = (a < b) ? a : b;
        }
    }
    return st;
}
