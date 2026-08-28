#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define ALIGNMENT 16
#define ALIGN(size) (((size) + (ALIGNMENT - 1)) & ~(ALIGNMENT - 1))

#define PREV_INUSE_FLAG 0x1
#define SIZE_MASK (~(size_t)(ALIGNMENT - 1))

#define HEAP_CAPACITY (256 * 1024) // 256 КіБ тестової пам'яті
#define NUM_BINS 8

typedef struct BlockHeader {
    size_t prev_size; // Використовується, лише якщо попередній блок вільний
    size_t size_flags; // Розмір блоку + прапорець PREV_INUSE у молодшому біті
    struct BlockHeader* next_free; // Вбудований покажчик на наступний вільний блок
    struct BlockHeader* prev_free; // Вбудований покажчик на попередній вільний блок
} BlockHeader;

#define HEADER_OVERHEAD (sizeof(size_t) * 2) // 16 байтів на заголовок
#define MIN_BLOCK_SIZE (ALIGN(sizeof(BlockHeader)))

typedef struct {
    uint8_t memory[HEAP_CAPACITY];
    BlockHeader* bins[NUM_BINS];
} SimpleAllocator;

static inline size_t get_size(const BlockHeader* b) {
    return b->size_flags & SIZE_MASK;
}

static inline bool is_prev_inuse(const BlockHeader* b) {
    return (b->size_flags & PREV_INUSE_FLAG) != 0;
}

static inline void set_size_and_flags(BlockHeader* b, size_t size, bool prev_inuse) {
    b->size_flags = (size & SIZE_MASK) | (prev_inuse ? PREV_INUSE_FLAG : 0);
}

static int get_bin_index(size_t size) {
    if (size <= 64)   return 0;
    if (size <= 128)  return 1;
    if (size <= 256)  return 2;
    if (size <= 512)  return 3;
    if (size <= 1024) return 4;
    if (size <= 4096) return 5;
    if (size <= 16384) return 6;
    return 7;
}

static void bin_insert(SimpleAllocator* a, BlockHeader* b) {
    int idx = get_bin_index(get_size(b));
    b->next_free = a->bins[idx];
    b->prev_free = NULL;
    if (a->bins[idx] != NULL) {
        a->bins[idx]->prev_free = b;
    }
    a->bins[idx] = b;
}

static void bin_remove(SimpleAllocator* a, BlockHeader* b) {
    int idx = get_bin_index(get_size(b));
    if (b->prev_free != NULL) {
        b->prev_free->next_free = b->next_free;
    } else {
        a->bins[idx] = b->next_free;
    }
    if (b->next_free != NULL) {
        b->next_free->prev_free = b->prev_free;
    }
    b->next_free = NULL;
    b->prev_free = NULL;
}

void allocator_init(SimpleAllocator* a) {
    memset(a->bins, 0, sizeof(a->bins));

    BlockHeader* initial = (BlockHeader*)a->memory;
    set_size_and_flags(initial, HEAP_CAPACITY, true);
    initial->prev_size = 0;
    initial->next_free = NULL;
    initial->prev_free = NULL;

    bin_insert(a, initial);
}

void* my_malloc(SimpleAllocator* a, size_t size) {
    if (size == 0) return NULL;

    size_t total_size = ALIGN(size + HEADER_OVERHEAD);
    if (total_size < MIN_BLOCK_SIZE) total_size = MIN_BLOCK_SIZE;

    int start_bin = get_bin_index(total_size);
    BlockHeader* victim = NULL;

    for (int i = start_bin; i < NUM_BINS; ++i) {
        BlockHeader* curr = a->bins[i];
        while (curr != NULL) {
            if (get_size(curr) >= total_size) {
                victim = curr;
                break;
            }
            curr = curr->next_free;
        }
        if (victim != NULL) break;
    }

    if (victim == NULL) return NULL; // OOM або фрагментація

    bin_remove(a, victim);
    size_t victim_size = get_size(victim);
    size_t remainder_size = victim_size - total_size;

    if (remainder_size >= MIN_BLOCK_SIZE) {
        // Розбиття (Splitting)
        set_size_and_flags(victim, total_size, is_prev_inuse(victim));

        BlockHeader* remainder = (BlockHeader*)((uint8_t*)victim + total_size);
        set_size_and_flags(remainder, remainder_size, true); // Попередній (victim) зайнятий
        remainder->prev_size = total_size;

        // Оновлюємо футер для сусіда remainder
        if ((uint8_t*)remainder + remainder_size < a->memory + HEAP_CAPACITY) {
            BlockHeader* next_phys = (BlockHeader*)((uint8_t*)remainder + remainder_size);
            next_phys->prev_size = remainder_size;
        }

        bin_insert(a, remainder);
    } else {
        // Віддаємо блок цілком
        if ((uint8_t*)victim + victim_size < a->memory + HEAP_CAPACITY) {
            BlockHeader* next_phys = (BlockHeader*)((uint8_t*)victim + victim_size);
            next_phys->size_flags |= PREV_INUSE_FLAG;
        }
    }

    // Повертаємо покажчик на корисні дані (одразу за заголовком)
    return (void*)((uint8_t*)victim + HEADER_OVERHEAD);
}

void my_free(SimpleAllocator* a, void* ptr) {
    if (ptr == NULL) return;

    BlockHeader* b = (BlockHeader*)((uint8_t*)ptr - HEADER_OVERHEAD);
    size_t size = get_size(b);
    bool prev_inuse = is_prev_inuse(b);

    // 1. Коалесценція назад (Backward coalescing)
    if (!prev_inuse) {
        BlockHeader* prev_block = (BlockHeader*)((uint8_t*)b - b->prev_size);
        bin_remove(a, prev_block);
        size += get_size(prev_block);
        prev_inuse = is_prev_inuse(prev_block);
        b = prev_block;
    }

    // 2. Коалесценція вперед (Forward coalescing)
    BlockHeader* next_block = (BlockHeader*)((uint8_t*)b + size);
    if ((uint8_t*)next_block < a->memory + HEAP_CAPACITY) {
        // Перевіряємо, чи вільний наступний блок
        BlockHeader* next_next = (BlockHeader*)((uint8_t*)next_block + get_size(next_block));
        bool next_is_free = true;
        if ((uint8_t*)next_next < a->memory + HEAP_CAPACITY) {
            next_is_free = !is_prev_inuse(next_next);
        }

        if (next_is_free) {
            bin_remove(a, next_block);
            size += get_size(next_block);
        } else {
            // Наступний блок зайнятий: скидаємо його PREV_INUSE у 0
            next_block->size_flags &= ~PREV_INUSE_FLAG;
            next_block->prev_size = size;
        }
    }

    set_size_and_flags(b, size, prev_inuse);

    // Оновлюємо футер вільного блоку для його правого сусіда
    BlockHeader* next_phys = (BlockHeader*)((uint8_t*)b + size);
    if ((uint8_t*)next_phys < a->memory + HEAP_CAPACITY) {
        next_phys->prev_size = size;
        next_phys->size_flags &= ~PREV_INUSE_FLAG;
    }

    bin_insert(a, b);
}
