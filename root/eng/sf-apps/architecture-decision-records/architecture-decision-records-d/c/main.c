/*
 * Фіксовані блоки пам'яті для телеметрії без malloc().
 * Обґрунтування та аналіз відкинутих варіантів: doc/adr/0005-static-can-pools.md
 *
 * Контекст: купа фрагментується на пікових навантаженнях CAN-шини.
 * Статичний пул виділяє блок за O(1) через бітову маску (find-first-set).
 */

#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define POOL_CAPACITY 32U
#define BLOCK_PAYLOAD_SIZE 64U

typedef struct {
    uint8_t payload[BLOCK_PAYLOAD_SIZE];
    uint16_t length;
    uint32_t timestamp_us;
} PacketBlock;

typedef struct {
    PacketBlock blocks[POOL_CAPACITY];
    uint32_t allocated_mask; // біт = 1 означає, що блок зайнятий
} StaticPacketPool;

static StaticPacketPool g_telemetry_pool;

void pool_init(void) {
    g_telemetry_pool.allocated_mask = 0U;
    memset(g_telemetry_pool.blocks, 0, sizeof(g_telemetry_pool.blocks));
}

PacketBlock* pool_acquire(void) {
    // Атомарний пошук першого нульового біта (O(1)):
    uint32_t mask = g_telemetry_pool.allocated_mask;
    if (mask == 0xFFFFFFFFU) {
        return NULL; // Пул вичерпано — лічильник переповнення інкрементується в caller
    }

    uint32_t free_index = (uint32_t)__builtin_ctz(~mask);
    g_telemetry_pool.allocated_mask |= (1UL << free_index);

    return &g_telemetry_pool.blocks[free_index];
}

void pool_release(const PacketBlock* block) {
    if (block == NULL) {
        return;
    }
    ptrdiff_t index = block - g_telemetry_pool.blocks;
    if (index >= 0 && index < (ptrdiff_t)POOL_CAPACITY) {
        g_telemetry_pool.allocated_mask &= ~(1UL << (uint32_t)index);
    }
}
