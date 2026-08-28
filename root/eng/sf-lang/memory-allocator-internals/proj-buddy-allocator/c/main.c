#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MIN_ORDER 10       // 2^10 = 1024 байти (1 КіБ)
#define MAX_ORDER 16       // 2^16 = 65536 байтів (64 КіБ)
#define NUM_ORDERS (MAX_ORDER - MIN_ORDER + 1)
#define POOL_SIZE (1 << MAX_ORDER)

typedef struct BlockNode {
    struct BlockNode* next;
} BlockNode;

typedef struct {
    uint8_t memory_pool[POOL_SIZE];
    BlockNode* free_lists[NUM_ORDERS];
    bool is_free[POOL_SIZE / (1 << MIN_ORDER)];
} BuddyAllocator;

static inline size_t order_to_size(int order_idx) {
    return (size_t)1 << (MIN_ORDER + order_idx);
}

static inline int size_to_order(size_t size) {
    size_t actual_size = 1 << MIN_ORDER;
    int order = 0;
    while (actual_size < size && order < NUM_ORDERS - 1) {
        actual_size <<= 1;
        order++;
    }
    return order;
}

void buddy_init(BuddyAllocator* alloc) {
    memset(alloc->free_lists, 0, sizeof(alloc->free_lists));
    memset(alloc->is_free, 0, sizeof(alloc->is_free));

    // Початковий стан: один нерозділений блок максимального порядку
    BlockNode* initial_block = (BlockNode*)alloc->memory_pool;
    initial_block->next = NULL;
    alloc->free_lists[NUM_ORDERS - 1] = initial_block;
    alloc->is_free[0] = true;
}

static void list_remove(BuddyAllocator* alloc, int order_idx, BlockNode* block) {
    BlockNode** curr = &alloc->free_lists[order_idx];
    while (*curr != NULL) {
        if (*curr == block) {
            *curr = block->next;
            return;
        }
        curr = &((*curr)->next);
    }
}

void* buddy_alloc(BuddyAllocator* alloc, size_t size) {
    if (size == 0 || size > POOL_SIZE) return NULL;

    int req_order = size_to_order(size);
    int current_order = req_order;

    // Шукаємо перший непорожній список відповідного або більшого порядку
    while (current_order < NUM_ORDERS && alloc->free_lists[current_order] == NULL) {
        current_order++;
    }

    if (current_order == NUM_ORDERS) {
        return NULL; // Вільна пам'ять потрібного розміру вичерпана
    }

    // Витягуємо блок із голови вільного списку
    BlockNode* block = alloc->free_lists[current_order];
    alloc->free_lists[current_order] = block->next;

    // Рекурсивно розбиваємо блок навпіл, поки не досягнемо потрібного порядку
    while (current_order > req_order) {
        current_order--;
        size_t half_size = order_to_size(current_order);
        BlockNode* buddy = (BlockNode*)((uint8_t*)block + half_size);
        
        buddy->next = alloc->free_lists[current_order];
        alloc->free_lists[current_order] = buddy;
        
        size_t buddy_idx = ((uint8_t*)buddy - alloc->memory_pool) >> MIN_ORDER;
        alloc->is_free[buddy_idx] = true;
    }

    size_t block_idx = ((uint8_t*)block - alloc->memory_pool) >> MIN_ORDER;
    alloc->is_free[block_idx] = false;

    return (void*)block;
}

void buddy_free(BuddyAllocator* alloc, void* ptr, size_t size) {
    if (ptr == NULL || size == 0) return;

    int order = size_to_order(size);
    uint8_t* block_addr = (uint8_t*)ptr;

    while (order < NUM_ORDERS - 1) {
        size_t block_size = order_to_size(order);
        size_t block_offset = block_addr - alloc->memory_pool;
        size_t buddy_offset = block_offset ^ block_size;
        uint8_t* buddy_addr = alloc->memory_pool + buddy_offset;

        size_t buddy_idx = buddy_offset >> MIN_ORDER;

        // Якщо близнюк зайнятий або належить іншому порядку — злиття неможливе
        if (!alloc->is_free[buddy_idx]) {
            break;
        }

        // Видаляємо близнюка з вільного списку
        list_remove(alloc, order, (BlockNode*)buddy_addr);
        alloc->is_free[buddy_idx] = false;

        // Початком злитого блоку стає менша адреса
        if (buddy_addr < block_addr) {
            block_addr = buddy_addr;
        }

        order++;
    }

    // Додаємо злитий блок у список відповідного вищого порядку
    BlockNode* free_block = (BlockNode*)block_addr;
    free_block->next = alloc->free_lists[order];
    alloc->free_lists[order] = free_block;

    size_t final_idx = (block_addr - alloc->memory_pool) >> MIN_ORDER;
    alloc->is_free[final_idx] = true;
}
