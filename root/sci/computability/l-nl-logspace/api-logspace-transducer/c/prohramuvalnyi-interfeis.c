/* C11 Static Arena Allocator contract for Logspace Execution */
#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

#define LOGSPACE_BUFFER_SIZE 4096 /* 4 KB fixed work tape */

typedef struct {
    uint8_t buffer[LOGSPACE_BUFFER_SIZE];
    size_t offset;
} LogspaceArena;

void logspace_arena_init(LogspaceArena *arena) {
    arena->offset = 0;
}

void* logspace_arena_alloc(LogspaceArena *arena, size_t bytes) {
    /* Align bytes to 8-byte boundary */
    size_t aligned_bytes = (bytes + 7) & ~((size_t)7);
    
    if (arena->offset + aligned_bytes > LOGSPACE_BUFFER_SIZE) {
        return NULL; /* Out of logspace buffer error! */
    }
    
    void *ptr = &arena->buffer[arena->offset];
    arena->offset += aligned_bytes;
    return ptr;
}

void logspace_arena_reset(LogspaceArena *arena) {
    arena->offset = 0;
}
