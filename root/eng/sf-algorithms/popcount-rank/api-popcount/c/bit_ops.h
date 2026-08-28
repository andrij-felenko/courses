/* bit_ops.h — Переносима бібліотека бітових операцій мовою C */
#ifndef BIT_OPS_H
#define BIT_OPS_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#if defined(_MSC_VER)
#  include <intrin.h>
#endif

#ifdef __cplusplus
extern "C" {
#endif

/* Статусні коди операцій вибірки та пошуку */
typedef enum {
    BIT_SUCCESS = 0,
    BIT_ERR_OUT_OF_RANGE = 1,
    BIT_ERR_NOT_FOUND = 2,
    BIT_ERR_INVALID_ARGUMENT = 3
} bit_status_t;

/* Обчислення ваги Гемінга (popcount) для 32-бітного слова */
static inline uint32_t bit_popcount32(uint32_t x) {
#if defined(__GNUC__) || defined(__clang__)
    return (uint32_t)__builtin_popcount(x);
#elif defined(_MSC_VER)
    return __popcnt(x);
#else
    /* Портативний безрозгалужений SWAR-алгоритм */
    x = x - ((x >> 1) & 0x55555555U);
    x = (x & 0x33333333U) + ((x >> 2) & 0x33333333U);
    x = (x + (x >> 4)) & 0x0F0F0F0FU;
    return (x * 0x01010101U) >> 24;
#endif
}

/* Обчислення ваги Гемінга (popcount) для 64-бітного слова */
static inline uint32_t bit_popcount64(uint64_t x) {
#if defined(__GNUC__) || defined(__clang__)
    return (uint32_t)__builtin_popcountll(x);
#elif defined(_MSC_VER) && defined(_M_X64)
    return (uint32_t)__popcnt64(x);
#elif defined(_MSC_VER)
    return __popcnt((uint32_t)x) + __popcnt((uint32_t)(x >> 32));
#else
    /* Портативний SWAR для 64-бітних слів */
    x = x - ((x >> 1) & 0x5555555555555555ULL);
    x = (x & 0x3333333333333333ULL) + ((x >> 2) & 0x3333333333333333ULL);
    x = (x + (x >> 4)) & 0x0F0F0F0F0F0F0F0FULL;
    return (uint32_t)((x * 0x0101010101010101ULL) >> 56);
#endif
}

/* Обчислення парності (1, якщо кількість одиниць непарна, 0 — якщо парна) */
static inline uint32_t bit_parity64(uint64_t x) {
#if defined(__GNUC__) || defined(__clang__)
    return (uint32_t)__builtin_parityll(x);
#else
    x ^= x >> 32;
    x ^= x >> 16;
    x ^= x >> 8;
    x ^= x >> 4;
    x ^= x >> 2;
    x ^= x >> 1;
    return (uint32_t)(x & 1ULL);
#endif
}

/* Обчислення рангу одиниць у 64-бітному слові на префіксі [0..bit_idx] */
static inline bit_status_t bit_rank64(uint64_t word, uint32_t bit_idx, uint32_t* out_rank) {
    if (!out_rank) return BIT_ERR_INVALID_ARGUMENT;
    if (bit_idx >= 64) {
        *out_rank = 0;
        return BIT_ERR_OUT_OF_RANGE;
    }
    uint64_t mask = (bit_idx == 63) ? ~0ULL : ((1ULL << (bit_idx + 1)) - 1ULL);
    *out_rank = bit_popcount64(word & mask);
    return BIT_SUCCESS;
}

/* Пошук позиції k-ї одиниці (1 <= k <= 64) у 64-бітному слові */
static inline bit_status_t bit_select64(uint64_t word, uint32_t k, uint32_t* out_pos) {
    if (!out_pos || k == 0 || k > 64) return BIT_ERR_INVALID_ARGUMENT;
    uint32_t total = bit_popcount64(word);
    if (k > total) {
        *out_pos = 0xFFFFFFFFU;
        return BIT_ERR_NOT_FOUND;
    }

    /* Двійковий пошук позиції k-ї одиниці за допомогою popcount */
    uint32_t low = 0, high = 63, result = 63;
    while (low <= high) {
        uint32_t mid = low + (high - low) / 2;
        uint64_t mask = (mid == 63) ? ~0ULL : ((1ULL << (mid + 1)) - 1ULL);
        if (bit_popcount64(word & mask) >= k) {
            result = mid;
            if (mid == 0) break;
            high = mid - 1;
        } else {
            low = mid + 1;
        }
    }
    *out_pos = result;
    return BIT_SUCCESS;
}

#ifdef __cplusplus
}
#endif

#endif /* BIT_OPS_H */
