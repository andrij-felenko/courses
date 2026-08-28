#include <stdint.h>
#include <stddef.h>

/* Фіксований статичний пул блоків у кастомній секції */
#define BLOCK_SIZE_BYTES  64
#define TOTAL_BLOCKS_NUM  32

__attribute__((section(".dma_buffer"), aligned(4)))
static uint8_t block_memory_pool[TOTAL_BLOCKS_NUM][BLOCK_SIZE_BYTES];
static uint32_t block_allocation_mask = 0;

void* FixedPool_Allocate(void) {
    for (uint32_t i = 0; i < TOTAL_BLOCKS_NUM; ++i) {
        if (!(block_allocation_mask & (1UL << i))) {
            block_allocation_mask |= (1UL << i);
            return (void*)&block_memory_pool[i][0];
        }
    }
    return NULL; /* Пам'ять у пулі вичерпана */
}

void FixedPool_Free(void *ptr) {
    if (ptr == NULL) return;
    ptrdiff_t offset = (uint8_t*)ptr - &block_memory_pool[0][0];
    uint32_t index = (uint32_t)(offset / BLOCK_SIZE_BYTES);
    if (index < TOTAL_BLOCKS_NUM) {
        block_allocation_mask &= ~(1UL << index);
    }
}
