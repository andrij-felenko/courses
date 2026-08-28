#include <stdlib.h>
#include <stdio.h>

#if defined(_WIN32)
#include <windows.h>
#else
#include <sys/mman.h>
#include <unistd.h>
#endif

typedef struct {
    uint8_t* buffer;
    size_t   capacity;
    size_t   size;
} ExecutableBuffer;

ExecutableBuffer* exec_buffer_create(size_t capacity) {
    ExecutableBuffer* eb = (ExecutableBuffer*)malloc(sizeof(ExecutableBuffer));
    if (!eb) return NULL;

    eb->capacity = capacity;
    eb->size = 0;

#if defined(_WIN32)
    eb->buffer = (uint8_t*)VirtualAlloc(NULL, capacity, 
                                        MEM_COMMIT | MEM_RESERVE, 
                                        PAGE_EXECUTE_READWRITE);
#else
    eb->buffer = (uint8_t*)mmap(NULL, capacity, 
                                PROT_READ | PROT_WRITE | PROT_EXEC, 
                                MAP_ANONYMOUS | MAP_PRIVATE, -1, 0);
    if (eb->buffer == MAP_FAILED) {
        free(eb);
        return NULL;
    }
#endif
    return eb;
}

void exec_buffer_free(ExecutableBuffer* eb) {
    if (!eb) return;
#if defined(_WIN32)
    VirtualFree(eb->buffer, 0, MEM_RELEASE);
#else
    munmap(eb->buffer, eb->capacity);
#endif
    free(eb);
}

uint8_t* exec_buffer_alloc_block(ExecutableBuffer* eb, size_t block_bytes) {
    if (eb->size + block_bytes > eb->capacity) {
        return NULL; // Переповнення буфера кешу коду
    }
    uint8_t* ptr = eb->buffer + eb->size;
    eb->size += block_bytes;
    return ptr;
}
