#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

#define BITSET_NOT_FOUND ((size_t)-1)

typedef struct {
    uint64_t *words;
    size_t num_bits;
    size_t num_words;
} BitSet;

static inline size_t bitset_calc_words(size_t bits) {
    return (bits + 63) / 64;
}

static inline uint64_t bitset_get_tail_mask(size_t bits) {
    size_t rem = bits & 63;
    return rem == 0 ? ~0ULL : ((1ULL << rem) - 1ULL);
}

BitSet* bitset_create(size_t num_bits) {
    BitSet *bs = (BitSet*)malloc(sizeof(BitSet));
    if (!bs) return NULL;

    bs->num_bits = num_bits;
    bs->num_words = bitset_calc_words(num_bits);
    
    /* Виділяємо та обнуляємо пам'ять під слова */
    bs->words = (uint64_t*)calloc(bs->num_words > 0 ? bs->num_words : 1, sizeof(uint64_t));
    if (!bs->words) {
        free(bs);
        return NULL;
    }
    return bs;
}

void bitset_destroy(BitSet *bs) {
    if (bs) {
        free(bs->words);
        free(bs);
    }
}

void bitset_set(BitSet *bs, size_t i) {
    if (i < bs->num_bits) {
        bs->words[i >> 6] |= (1ULL << (i & 63));
    }
}

void bitset_clear(BitSet *bs, size_t i) {
    if (i < bs->num_bits) {
        bs->words[i >> 6] &= ~(1ULL << (i & 63));
    }
}

bool bitset_test(const BitSet *bs, size_t i) {
    if (i >= bs->num_bits) return false;
    return (bs->words[i >> 6] & (1ULL << (i & 63))) != 0;
}

void bitset_fill_zeros(BitSet *bs) {
    if (bs->num_words > 0) {
        memset(bs->words, 0, bs->num_words * sizeof(uint64_t));
    }
}

void bitset_fill_ones(BitSet *bs) {
    if (bs->num_words == 0) return;
    memset(bs->words, 0xFF, bs->num_words * sizeof(uint64_t));
    /* Очищуємо зайві біти в останньому слові */
    bs->words[bs->num_words - 1] &= bitset_get_tail_mask(bs->num_bits);
}

/* Підрахунок потужності множини через апаратний POPCNT */
size_t bitset_popcount(const BitSet *bs) {
    size_t total = 0;
    for (size_t w = 0; w < bs->num_words; ++w) {
        total += (size_t)__builtin_popcountll(bs->words[w]);
    }
    return total;
}

/* Пошук першого встановленого біта (найменшого елемента) через CTZ */
size_t bitset_find_first(const BitSet *bs) {
    for (size_t w = 0; w < bs->num_words; ++w) {
        uint64_t val = bs->words[w];
        if (val != 0) {
            size_t bit_pos = (w << 6) + (size_t)__builtin_ctzll(val);
            return (bit_pos < bs->num_bits) ? bit_pos : BITSET_NOT_FOUND;
        }
    }
    return BITSET_NOT_FOUND;
}

/* Пошук наступного встановленого біта після поточної позиції curr */
size_t bitset_find_next(const BitSet *bs, size_t curr) {
    size_t next_idx = curr + 1;
    if (next_idx >= bs->num_bits) return BITSET_NOT_FOUND;

    size_t w = next_idx >> 6;
    size_t offset = next_idx & 63;

    /* Маскуємо вже пройдені молодші біти в поточному слові */
    uint64_t val = bs->words[w] & (~0ULL << offset);
    if (val != 0) {
        size_t bit_pos = (w << 6) + (size_t)__builtin_ctzll(val);
        return (bit_pos < bs->num_bits) ? bit_pos : BITSET_NOT_FOUND;
    }

    /* Скануємо наступні слова */
    for (w = w + 1; w < bs->num_words; ++w) {
        val = bs->words[w];
        if (val != 0) {
            size_t bit_pos = (w << 6) + (size_t)__builtin_ctzll(val);
            return (bit_pos < bs->num_bits) ? bit_pos : BITSET_NOT_FOUND;
        }
    }
    return BITSET_NOT_FOUND;
}

/* Операції над множинами: dst = dst OP src */
bool bitset_intersect(BitSet *dst, const BitSet *src) {
    if (dst->num_bits != src->num_bits) return false;
    for (size_t w = 0; w < dst->num_words; ++w) {
        dst->words[w] &= src->words[w];
    }
    return true;
}

bool bitset_union(BitSet *dst, const BitSet *src) {
    if (dst->num_bits != src->num_bits) return false;
    for (size_t w = 0; w < dst->num_words; ++w) {
        dst->words[w] |= src->words[w];
    }
    dst->words[dst->num_words - 1] &= bitset_get_tail_mask(dst->num_bits);
    return true;
}

bool bitset_difference(BitSet *dst, const BitSet *src) {
    if (dst->num_bits != src->num_bits) return false;
    for (size_t w = 0; w < dst->num_words; ++w) {
        dst->words[w] &= ~src->words[w];
    }
    return true;
}
