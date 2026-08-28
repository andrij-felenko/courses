#include <string.h>

#define WORD_BITS 32
static uint32_t used_map[(POOL_BLOCKS + WORD_BITS - 1) / WORD_BITS];

static inline size_t blk_index(const void *blk) {
    return (size_t)((const uint8_t *)blk - &pool_mem[0][0]) / POOL_BLOCK_SZ;
}
static inline bool bit_get(size_t i) {
    return (used_map[i / WORD_BITS] >> (i % WORD_BITS)) & 1u;
}
static inline void bit_set(size_t i) {
    used_map[i / WORD_BITS] |=  (1u << (i % WORD_BITS));
}
static inline void bit_clr(size_t i) {
    used_map[i / WORD_BITS] &= ~(1u << (i % WORD_BITS));
}
