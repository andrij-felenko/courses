/* Простий арена-алокатор для пулу кошиків */
typedef struct {
    uint8_t *buffer;
    size_t capacity;
    size_t offset;
} memory_arena_t;

memory_arena_t arena_create(size_t capacity) {
    memory_arena_t a;
    a.buffer = (uint8_t*)malloc(capacity);
    a.capacity = capacity;
    a.offset = 0;
    return a;
}

void* arena_alloc(memory_arena_t *a, size_t size, size_t align) {
    size_t aligned_offset = (a->offset + (align - 1)) & ~(align - 1);
    if (aligned_offset + size > a->capacity) {
        return NULL;
    }
    void *ptr = &a->buffer[aligned_offset];
    a->offset = aligned_offset + size;
    return ptr;
}

void arena_reset(memory_arena_t *a) {
    a->offset = 0;
}

void arena_destroy(memory_arena_t *a) {
    free(a->buffer);
    a->buffer = NULL;
}
