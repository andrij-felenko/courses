#include <sanitizer/asan_interface.h>
#include <stdlib.h>
#include <stddef.h>

typedef struct {
    char buffer[1024];
    size_t allocated;
} SimpleArena;

void arena_init(SimpleArena *arena) {
    arena->allocated = 0;
    // Початково отруюємо весь буфер арени
    ASAN_POISON_MEMORY_REGION(arena->buffer, sizeof(arena->buffer));
}

void *arena_alloc(SimpleArena *arena, size_t size) {
    if (arena->allocated + size > sizeof(arena->buffer)) {
        return NULL;
    }
    void *ptr = &arena->buffer[arena->allocated];
    arena->allocated += size;
    // Знімаємо отруєння лише з тих байтів, які віддаються клієнту
    ASAN_UNPOISON_MEMORY_REGION(ptr, size);
    return ptr;
}
