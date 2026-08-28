#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#define BLOCK_SIZE  64
#define BLOCK_COUNT 16

typedef struct BlockNode {
    struct BlockNode* next;
} BlockNode;

typedef struct {
    uint8_t storage[BLOCK_COUNT * BLOCK_SIZE];
    BlockNode* free_head;
} MemoryPoolC;

void pool_init_c(MemoryPoolC* pool) {
    pool->free_head = NULL;
    for (size_t i = 0; i < BLOCK_COUNT; ++i) {
        BlockNode* node = (BlockNode*)&pool->storage[i * BLOCK_SIZE];
        node->next = pool->free_head;
        pool->free_head = node;
    }
}

void* pool_allocate_c(MemoryPoolC* pool) {
    if (pool->free_head == NULL) return NULL;
    BlockNode* node = pool->free_head;
    pool->free_head = node->next;
    return (void*)node;
}

void pool_deallocate_c(MemoryPoolC* pool, void* ptr) {
    if (ptr == NULL) return;
    BlockNode* node = (BlockNode*)ptr;
    node->next = pool->free_head;
    pool->free_head = node;
}
