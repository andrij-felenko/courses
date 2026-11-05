#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define DEDUP_RING_SIZE         64U   /* Розмір кільцевого буфера FIFO (ступінь 2) */
#define DEDUP_HASH_SIZE         128U  /* Розмір хеш-таблиці (ступінь 2) */
#define DEDUP_HASH_MASK         (DEDUP_HASH_SIZE - 1U)
#define DEDUP_MAX_PROBES        8U    /* Межа лінійного зондування */
#define DEDUP_MAX_PAYLOAD       16U   /* Розмір буфера збереженої відповіді */

#define HW_CRC_BASE             (0x40023000UL)
#define HW_CRC_DR               (*(volatile uint32_t*)(HW_CRC_BASE + 0x00U))
#define HW_CRC_CR               (*(volatile uint32_t*)(HW_CRC_BASE + 0x08U))

#define CORE_DEMCR              (*(volatile uint32_t*)0xE000EDFCUL)
#define DWT_CTRL                (*(volatile uint32_t*)0xE0001000UL)
#define DWT_CYCCNT              (*(volatile uint32_t*)0xE0001004UL)

typedef enum {
    TX_FREE = 0,
    TX_IN_PROGRESS,
    TX_COMMITTED,
    TX_ABORTED
} HwTxState_t;

typedef struct __attribute__((aligned(32))) {
    uint32_t tx_id;
    uint32_t timestamp_cycles;
    uint16_t sender_id;
    uint8_t  state;
    uint8_t  response_len;
    uint8_t  response[DEDUP_MAX_PAYLOAD];
    uint8_t  reserved[4];
} HwTxDescriptor_t;

typedef struct {
    HwTxDescriptor_t ring[DEDUP_RING_SIZE];
    uint16_t hash_buckets[DEDUP_HASH_SIZE];
    volatile uint32_t head_index;
} HwDedupCache_t;

static HwDedupCache_t g_hw_cache __attribute__((aligned(32)));

static inline uint32_t atomic_load_exclusive(volatile uint32_t* addr) {
    uint32_t result;
    __asm volatile ("ldrex %0, [%1]" : "=r" (result) : "r" (addr) : "memory");
    return result;
}

static inline uint32_t atomic_store_exclusive(volatile uint32_t* addr, uint32_t value) {
    uint32_t result;
    __asm volatile ("strex %0, %1, [%2]" : "=&r" (result) : "r" (value), "r" (addr) : "memory");
    return result;
}

static inline void memory_barrier_dmb(void) {
    __asm volatile ("dmb 0xF" ::: "memory");
}

void hw_dedup_init(void) {
    CORE_DEMCR |= (1UL << 24);
    DWT_CYCCNT = 0U;
    DWT_CTRL |= (1UL << 0);
    HW_CRC_CR = 1U;

    memset(&g_hw_cache, 0, sizeof(g_hw_cache));
    for (uint32_t i = 0; i < DEDUP_HASH_SIZE; i++) {
        g_hw_cache.hash_buckets[i] = 0xFFFFU;
    }
}

uint32_t hw_dedup_calculate_crc(const uint32_t* words, size_t count) {
    HW_CRC_CR = 1U;
    for (size_t i = 0; i < count; i++) {
        HW_CRC_DR = words[i];
    }
    return HW_CRC_DR;
}

HwTxState_t hw_dedup_check_and_claim(uint32_t tx_id, uint16_t sender_id, uint16_t* allocated_slot) {
    uint16_t start_bucket = (uint16_t)(tx_id & DEDUP_HASH_MASK);

    for (uint16_t probe = 0; probe < DEDUP_MAX_PROBES; probe++) {
        uint16_t bucket = (uint16_t)((start_bucket + probe) & DEDUP_HASH_MASK);
        uint16_t slot = g_hw_cache.hash_buckets[bucket];

        if (slot == 0xFFFFU) {
            break;
        }

        HwTxDescriptor_t* desc = &g_hw_cache.ring[slot];
        if (desc->tx_id == tx_id && desc->sender_id == sender_id && desc->state != TX_FREE) {
            *allocated_slot = slot;
            return (HwTxState_t)desc->state;
        }
    }

    uint32_t current_head, next_head;
    do {
        current_head = atomic_load_exclusive(&g_hw_cache.head_index);
        next_head = (current_head + 1U) & (DEDUP_RING_SIZE - 1U);
    } while (atomic_store_exclusive(&g_hw_cache.head_index, next_head) != 0U);

    uint16_t new_slot = (uint16_t)current_head;
    HwTxDescriptor_t* target = &g_hw_cache.ring[new_slot];

    if (target->state != TX_FREE) {
        uint16_t old_bucket = (uint16_t)(target->tx_id & DEDUP_HASH_MASK);
        for (uint16_t probe = 0; probe < DEDUP_MAX_PROBES; probe++) {
            uint16_t b = (uint16_t)((old_bucket + probe) & DEDUP_HASH_MASK);
            if (g_hw_cache.hash_buckets[b] == new_slot) {
                g_hw_cache.hash_buckets[b] = 0xFFFFU;
                break;
            }
        }
    }

    target->tx_id = tx_id;
    target->sender_id = sender_id;
    target->timestamp_cycles = DWT_CYCCNT;
    target->response_len = 0;
    target->state = TX_IN_PROGRESS;

    for (uint16_t probe = 0; probe < DEDUP_MAX_PROBES; probe++) {
        uint16_t b = (uint16_t)((start_bucket + probe) & DEDUP_HASH_MASK);
        if (g_hw_cache.hash_buckets[b] == 0xFFFFU) {
            g_hw_cache.hash_buckets[b] = new_slot;
            break;
        }
    }

    memory_barrier_dmb();
    *allocated_slot = new_slot;
    return TX_FREE;
}

void hw_dedup_commit_result(uint16_t slot, const uint8_t* data, uint8_t len) {
    if (slot >= DEDUP_RING_SIZE) return;

    HwTxDescriptor_t* desc = &g_hw_cache.ring[slot];
    if (len > DEDUP_MAX_PAYLOAD) {
        len = DEDUP_MAX_PAYLOAD;
    }
    memcpy(desc->response, data, len);
    desc->response_len = len;

    memory_barrier_dmb();
    desc->state = TX_COMMITTED;
}
