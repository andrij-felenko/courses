/* rank_bitset.h / rank_bitset.c — Промислова реалізація бітового вектора мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#if defined(_MSC_VER)
#  include <intrin.h>
#  include <malloc.h>
#  define POPCOUNT64 __popcnt64
#else
#  include <immintrin.h>
#  define POPCOUNT64 __builtin_popcountll
#endif

/* Виділення пам'яті з вирівнюванням за межею 64 байти */
static void* aligned_alloc_64(size_t size) {
    size_t aligned_size = (size + 63) & ~63ULL;
#if defined(_MSC_VER)
    return _aligned_malloc(aligned_size, 64);
#elif defined(_POSIX_C_SOURCE) && _POSIX_C_SOURCE >= 200112L
    void* ptr = NULL;
    if (posix_memalign(&ptr, 64, aligned_size) != 0) return NULL;
    return ptr;
#else
    void* raw = malloc(aligned_size + 64 + sizeof(void*));
    if (!raw) return NULL;
    uintptr_t base = (uintptr_t)raw + sizeof(void*);
    void* aligned = (void*)((base + 63) & ~63ULL);
    ((void**)aligned)[-1] = raw;
    return aligned;
#endif
}

static void aligned_free_64(void* ptr) {
    if (!ptr) return;
#if defined(_MSC_VER)
    _aligned_free(ptr);
#elif defined(_POSIX_C_SOURCE) && _POSIX_C_SOURCE >= 200112L
    free(ptr);
#else
    free(((void**)ptr)[-1]);
#endif
}

/* Індексний блок Rank9: 16 байтів на кожні 512 бітів даних */
typedef struct {
    uint64_t abs_rank;  /* Абсолютна сума одиниць до початку суперблока */
    uint64_t offsets;   /* 7 упакованих 9-бітних лічильників */
} Rank9Block;

typedef struct {
    uint64_t* data;         /* Масив 64-бітних слів бітового вектора */
    Rank9Block* index;      /* Дворівневий індекс Rank9 */
    size_t num_bits;        /* Загальна кількість корисних бітів */
    size_t num_words;       /* Кількість 64-бітних слів даних */
    size_t num_blocks;      /* Кількість 512-бітних суперблоків */
    uint64_t total_ones;    /* Загальна кількість встановлених одиниць */
    bool index_built;       /* Прапорець актуальності побудованого індексу */
} RankBitSet;

/* Створення та ініціалізація структури */
RankBitSet* rank_bitset_create(size_t num_bits) {
    if (num_bits == 0) return NULL;

    RankBitSet* bs = (RankBitSet*)malloc(sizeof(RankBitSet));
    if (!bs) return NULL;

    bs->num_bits = num_bits;
    bs->num_words = (num_bits + 63) / 64;
    bs->num_blocks = (num_bits + 511) / 512;
    bs->total_ones = 0;
    bs->index_built = false;

    /* Виділяємо буфери з вирівнюванням під розмір рядка кеша */
    size_t alloc_words = bs->num_blocks * 8;
    bs->data = (uint64_t*)aligned_alloc_64(alloc_words * sizeof(uint64_t));
    bs->index = (Rank9Block*)aligned_alloc_64(bs->num_blocks * sizeof(Rank9Block));

    if (!bs->data || !bs->index) {
        aligned_free_64(bs->data);
        aligned_free_64(bs->index);
        free(bs);
        return NULL;
    }

    memset(bs->data, 0, alloc_words * sizeof(uint64_t));
    memset(bs->index, 0, bs->num_blocks * sizeof(Rank9Block));
    return bs;
}

/* Звільнення ресурсів */
void rank_bitset_destroy(RankBitSet* bs) {
    if (bs) {
        aligned_free_64(bs->data);
        aligned_free_64(bs->index);
        free(bs);
    }
}

/* Встановлення біта в 1 */
void rank_bitset_set(RankBitSet* bs, size_t bit_idx) {
    if (bit_idx < bs->num_bits) {
        bs->data[bit_idx / 64] |= (1ULL << (bit_idx % 64));
        bs->index_built = false;
    }
}

/* Перевірка значення біта */
bool rank_bitset_test(const RankBitSet* bs, size_t bit_idx) {
    if (bit_idx >= bs->num_bits) return false;
    return (bs->data[bit_idx / 64] & (1ULL << (bit_idx % 64))) != 0;
}

/* Побудова індексу Rank9 за O(N) */
void rank_bitset_build(RankBitSet* bs) {
    uint64_t running_total = 0;

    for (size_t b = 0; b < bs->num_blocks; b++) {
        bs->index[b].abs_rank = running_total;
        uint64_t packed_offsets = 0;
        uint64_t block_sum = 0;

        /* Лічильники для слів 1..7 усередині суперблока */
        for (int w = 0; w < 7; w++) {
            size_t word_idx = b * 8 + w;
            uint64_t word_val = bs->data[word_idx];
            block_sum += POPCOUNT64(word_val);
            packed_offsets |= (block_sum & 0x1FFULL) << (w * 9);
        }

        bs->index[b].offsets = packed_offsets;

        /* Враховуємо останнє (8-ме) слово суперблока */
        size_t last_word_idx = b * 8 + 7;
        block_sum += POPCOUNT64(bs->data[last_word_idx]);
        running_total += block_sum;
    }

    bs->total_ones = running_total;
    bs->index_built = true;
}

/* Запит rank1(i): кількість одиниць у [0..bit_idx] за O(1) */
size_t rank_bitset_rank1(const RankBitSet* bs, size_t bit_idx) {
    if (bit_idx >= bs->num_bits) {
        bit_idx = bs->num_bits - 1;
    }

    size_t block_idx = bit_idx / 512;
    size_t word_in_block = (bit_idx % 512) / 64;
    size_t bit_in_word = bit_idx % 64;

    /* 1. Базовий ранг суперблока */
    uint64_t rank = bs->index[block_idx].abs_rank;

    /* 2. Відносне зміщення слова у суперблоці */
    if (word_in_block > 0) {
        int shift = (int)(word_in_block - 1) * 9;
        rank += (bs->index[block_idx].offsets >> shift) & 0x1FFULL;
    }

    /* 3. Залишок у поточному слові через маскування */
    uint64_t word = bs->data[block_idx * 8 + word_in_block];
    uint64_t mask = (bit_in_word == 63) ? ~0ULL : ((1ULL << (bit_in_word + 1)) - 1ULL);
    rank += POPCOUNT64(word & mask);

    return (size_t)rank;
}

/* Дуальний ранг нулів rank0(i) */
size_t rank_bitset_rank0(const RankBitSet* bs, size_t bit_idx) {
    if (bit_idx >= bs->num_bits) bit_idx = bs->num_bits - 1;
    return (bit_idx + 1) - rank_bitset_rank1(bs, bit_idx);
}

/* Запит select1(k): знаходження позиції k-ї одиниці (1-індексація) */
size_t rank_bitset_select1(const RankBitSet* bs, size_t k) {
    if (k == 0 || k > bs->total_ones) return (size_t)-1;

    /* Двійковий пошук потрібного суперблока */
    size_t low = 0, high = bs->num_blocks - 1, target_block = 0;
    while (low <= high) {
        size_t mid = low + (high - low) / 2;
        if (bs->index[mid].abs_rank < k) {
            target_block = mid;
            low = mid + 1;
        } else {
            if (mid == 0) break;
            high = mid - 1;
        }
    }

    /* Локалізація слова всередині суперблока */
    uint64_t k_rem = k - bs->index[target_block].abs_rank;
    size_t target_word = 0;
    uint64_t prev_offset = 0;

    for (int w = 1; w < 8; w++) {
        uint64_t cur_offset = (w == 8) ? (uint64_t)-1 : 
            ((w < 8) ? ((bs->index[target_block].offsets >> ((w - 1) * 9)) & 0x1FFULL) : 0);
        
        if (w == 7) {
            uint64_t w6_val = bs->data[target_block * 8 + 6];
            cur_offset = ((bs->index[target_block].offsets >> (5 * 9)) & 0x1FFULL) + POPCOUNT64(w6_val);
        }

        if (cur_offset >= k_rem) {
            target_word = (size_t)(w - 1);
            break;
        }
        prev_offset = cur_offset;
        if (w == 7) target_word = 7;
    }

    uint64_t in_word_k = k_rem - prev_offset;
    uint64_t word_val = bs->data[target_block * 8 + target_word];

    /* Бінарний пошук біта у слові */
    uint32_t b_low = 0, b_high = 63, b_res = 63;
    while (b_low <= b_high) {
        uint32_t mid = b_low + (b_high - b_low) / 2;
        uint64_t mask = (mid == 63) ? ~0ULL : ((1ULL << (mid + 1)) - 1ULL);
        if (POPCOUNT64(word_val & mask) >= in_word_k) {
            b_res = mid;
            if (mid == 0) break;
            b_high = mid - 1;
        } else {
            b_low = mid + 1;
        }
    }

    return target_block * 512 + target_word * 64 + b_res;
}

/* Векторизований підрахунок великих масивів за алгоритмом Харлі-Сіла (3:2 CSA) */
uint64_t rank_bitset_popcount_csa(const uint64_t* data, size_t num_words) {
    uint64_t total = 0;
    size_t i = 0;

    while (i + 2 < num_words) {
        uint64_t a = data[i];
        uint64_t b = data[i + 1];
        uint64_t c = data[i + 2];

        uint64_t sum = a ^ b ^ c;
        uint64_t carry = (a & b) | (b & c) | (c & a);

        total += POPCOUNT64(sum);
        total += 2ULL * POPCOUNT64(carry);
        i += 3;
    }

    while (i < num_words) {
        total += POPCOUNT64(data[i]);
        i++;
    }
    return total;
}
