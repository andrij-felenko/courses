#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

/* --- БЛОКОВИЙ ПУЛ ФІКСОВАНОГО РОЗМІРУ --- */

typedef struct pool_node {
    struct pool_node* next;
} pool_node_t;

typedef struct {
    uint8_t* buffer;        /* Вказівник на виділений статичний масив */
    size_t block_size;      /* Розмір одного блоку (вирівняний) */
    size_t block_count;     /* Загальна кількість блоків */
    pool_node_t* free_list; /* Голова списку вільних блоків */
    size_t free_count;      /* Поточна кількість вільних блоків */
    size_t min_free_count;  /* Водяний знак мінімального запасу блоків */
} fixed_pool_t;

/* Ініціалізація пула. Мінімальний розмір блоку не може бути меншим за sizeof(pool_node_t) */
bool pool_init(fixed_pool_t* pool, void* buffer, size_t block_size, size_t block_count) {
    if (!pool || !buffer || block_count == 0) {
        return false;
    }

    /* Вирівнювання розміру блоку до кратності покажчика машини (4 або 8 байтів) */
    size_t align = sizeof(uintptr_t);
    size_t aligned_block_size = (block_size + (align - 1)) & ~(align - 1);
    if (aligned_block_size < sizeof(pool_node_t)) {
        aligned_block_size = sizeof(pool_node_t);
    }

    pool->buffer = (uint8_t*)buffer;
    pool->block_size = aligned_block_size;
    pool->block_count = block_count;
    pool->free_count = block_count;
    pool->min_free_count = block_count;
    pool->free_list = NULL;

    /* Створення початкового зв'язного списку вільних блоків */
    for (size_t i = 0; i < block_count; ++i) {
        uint8_t* block_addr = pool->buffer + (i * aligned_block_size);
        pool_node_t* node = (pool_node_t*)block_addr;
        node->next = pool->free_list;
        pool->free_list = node;
    }

    return true;
}

/* Виділення одного блоку за O(1) */
void* pool_alloc(fixed_pool_t* pool) {
    if (!pool || !pool->free_list) {
        return NULL; /* Пул вичерпано */
    }

    pool_node_t* node = pool->free_list;
    pool->free_list = node->next;
    pool->free_count--;

    if (pool->free_count < pool->min_free_count) {
        pool->min_free_count = pool->free_count;
    }

    return (void*)node;
}

/* Звільнення блоку за O(1) з перевіркою адреси */
bool pool_free(fixed_pool_t* pool, void* ptr) {
    if (!pool || !ptr) {
        return false;
    }

    uint8_t* p = (uint8_t*)ptr;
    uint8_t* start = pool->buffer;
    uint8_t* end = pool->buffer + (pool->block_size * pool->block_count);

    /* Перевірка, що адреса належить цьому пулу і суворо вирівняна на крок блоку */
    if (p < start || p >= end) {
        return false;
    }
    ptrdiff_t offset = p - start;
    if ((offset % pool->block_size) != 0) {
        return false; /* Адреса вказує всередину блоку! */
    }

    pool_node_t* node = (pool_node_t*)ptr;
    node->next = pool->free_list;
    pool->free_list = node;
    pool->free_count++;

    return true;
}

/* --- ЛІНІЙНА АРЕНА ПАМ'ЯТІ --- */

typedef struct {
    uint8_t* buffer;
    size_t capacity;
    size_t offset;
    size_t peak_offset;
} memory_arena_t;

/* Ініціалізація арени */
bool arena_init(memory_arena_t* arena, void* buffer, size_t capacity) {
    if (!arena || !buffer || capacity == 0) {
        return false;
    }
    arena->buffer = (uint8_t*)buffer;
    arena->capacity = capacity;
    arena->offset = 0;
    arena->peak_offset = 0;
    return true;
}

/* Виділення пам'яті із заданим вирівнюванням за O(1) */
void* arena_alloc_aligned(memory_arena_t* arena, size_t size, size_t alignment) {
    if (!arena || size == 0) {
        return NULL;
    }
    if (alignment == 0 || (alignment & (alignment - 1)) != 0) {
        alignment = sizeof(uintptr_t); /* Стандартне вирівнювання */
    }

    uintptr_t current_addr = (uintptr_t)(arena->buffer + arena->offset);
    uintptr_t aligned_addr = (current_addr + (alignment - 1)) & ~(alignment - 1);
    size_t padding = aligned_addr - current_addr;

    if (arena->offset + padding + size > arena->capacity) {
        return NULL; /* Переповнення арени */
    }

    arena->offset += padding + size;
    if (arena->offset > arena->peak_offset) {
        arena->peak_offset = arena->offset;
    }

    return (void*)aligned_addr;
}

void* arena_alloc(memory_arena_t* arena, size_t size) {
    return arena_alloc_aligned(arena, size, sizeof(uintptr_t));
}

/* Збереження та відновлення контрольної точки */
size_t arena_save(const memory_arena_t* arena) {
    return arena ? arena->offset : 0;
}

void arena_restore(memory_arena_t* arena, size_t savepoint) {
    if (arena && savepoint <= arena->capacity) {
        arena->offset = savepoint;
    }
}

/* Повне скидання арени для нового кадру */
void arena_reset(memory_arena_t* arena) {
    if (arena) {
        arena->offset = 0;
    }
}
