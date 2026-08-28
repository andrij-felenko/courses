#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    uint64_t *words;
    size_t size;
} BitSet;

BitSet* bitset_create(size_t num_bits) {
    BitSet *bs = (BitSet*)malloc(sizeof(BitSet));
    size_t num_words = (num_bits + 63) / 64;
    bs->words = (uint64_t*)calloc(num_words, sizeof(uint64_t));
    bs->size = num_bits;
    return bs;
}

void bitset_set(BitSet *bs, size_t i) {
    bs->words[i >> 6] |= (1ULL << (i & 63));
}

void bitset_clear(BitSet *bs, size_t i) {
    bs->words[i >> 6] &= ~(1ULL << (i & 63));
}

bool bitset_test(const BitSet *bs, size_t i) {
    return (bs->words[i >> 6] & (1ULL << (i & 63))) != 0;
}

void bitset_free(BitSet *bs) {
    free(bs->words);
    free(bs);
}
