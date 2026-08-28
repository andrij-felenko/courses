#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <pthread.h>

#define ARENA_CHUNK_SIZE (64 * 1024) // 64 KB на потік

typedef struct ArenaChunk {
    uint8_t* buffer;
    size_t offset;
    size_t capacity;
    struct ArenaChunk* prev;
} ArenaChunk;

// Оголошення локального стану потоку в стилі C (GCC __thread / Clang)
static __thread ArenaChunk* current_thread_arena = NULL;

static ArenaChunk* arena_create_chunk(size_t cap, ArenaChunk* prev) {
    ArenaChunk* chunk = (ArenaChunk*)malloc(sizeof(ArenaChunk));
    if (!chunk) return NULL;
    chunk->buffer = (uint8_t*)malloc(cap);
    chunk->offset = 0;
    chunk->capacity = cap;
    chunk->prev = prev;
    return chunk;
}

void* thread_arena_alloc(size_t size, size_t alignment) {
    if (!current_thread_arena) {
        current_thread_arena = arena_create_chunk(ARENA_CHUNK_SIZE, NULL);
        if (!current_thread_arena) return NULL;
    }

    // Вирівнювання поточного зміщення
    size_t current_addr = (size_t)(current_thread_arena->buffer + current_thread_arena->offset);
    size_t aligned_addr = (current_addr + (alignment - 1)) & ~(alignment - 1);
    size_t new_offset = (aligned_addr - (size_t)current_thread_arena->buffer) + size;

    if (new_offset > current_thread_arena->capacity) {
        // Поточний чанк вичерпано — виділяємо новий чанк удвічі більшого розміру
        size_t next_cap = current_thread_arena->capacity * 2;
        if (next_cap < size + alignment) next_cap = size + alignment + ARENA_CHUNK_SIZE;
        current_thread_arena = arena_create_chunk(next_cap, current_thread_arena);
        if (!current_thread_arena) return NULL;
        return thread_arena_alloc(size, alignment);
    }

    void* ptr = (void*)aligned_addr;
    current_thread_arena->offset = new_offset;
    return ptr;
}

void thread_arena_reset(void) {
    // Скидання пам'яті до початкового чанка без повернення пам'яті ОС
    while (current_thread_arena && current_thread_arena->prev) {
        ArenaChunk* old = current_thread_arena;
        current_thread_arena = current_thread_arena->prev;
        free(old->buffer);
        free(old);
    }
    if (current_thread_arena) {
        current_thread_arena->offset = 0;
    }
}

void thread_arena_destroy(void) {
    while (current_thread_arena) {
        ArenaChunk* old = current_thread_arena;
        current_thread_arena = current_thread_arena->prev;
        free(old->buffer);
        free(old);
    }
}
