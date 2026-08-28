#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

/* Коефіцієнт просторового надлишку c = 1.23 */
#define XOR_FILTER_OVERHEAD_FACTOR 1.23
#define XOR_FILTER_MAX_ATTEMPTS 64

/* Структура 8-бітного Xor-фільтра */
typedef struct {
    uint64_t seed;          /* Псевдовипадковий засів хешування */
    uint32_t block_length;  /* Довжина одного з 3 блоків (L) */
    uint8_t *fingerprints;  /* Масив відбитків розміром 3 * block_length */
} xor_filter_8_t;

/* Допоміжна структура для стека лущення */
typedef struct {
    uint64_t key;
    uint32_t index;
} xor_peel_entry_t;

/* Швидкий 64-бітний хеш Murmur3/SplitMix64 */
static inline uint64_t xor_hash64(uint64_t x, uint64_t seed) {
    x ^= seed;
    x ^= x >> 33;
    x *= 0xff51afd7ed558ccdULL;
    x ^= x >> 33;
    x *= 0xc4ceb9fe1a85ec53ULL;
    x ^= x >> 33;
    return x;
}

/* Швидке зведення 64-бітного значення до діапазону [0, n) без ділення (Lemire FastRange) */
static inline uint32_t xor_reduce(uint32_t hash, uint32_t n) {
    return (uint32_t)(((uint64_t)hash * (uint64_t)n) >> 32);
}

/* Обчислення трьох індексів у трьох незалежних блоках B0, B1, B2 */
static inline void xor_get_positions(uint64_t key, uint64_t seed, uint32_t block_len,
                                     uint32_t *h0, uint32_t *h1, uint32_t *h2) {
    uint64_t hash = xor_hash64(key, seed);
    uint32_t a = (uint32_t)(hash >> 32);
    uint32_t b = (uint32_t)hash;
    uint32_t c = (uint32_t)(hash ^ (hash >> 16));

    *h0 = xor_reduce(a, block_len);
    *h1 = block_len + xor_reduce(b, block_len);
    *h2 = 2 * block_len + xor_reduce(c, block_len);
}

/* Обчислення 8-бітного цільового відбитка */
static inline uint8_t xor_fingerprint(uint64_t key, uint64_t seed) {
    uint64_t hash = xor_hash64(key, ~seed);
    uint8_t fp = (uint8_t)(hash ^ (hash >> 32));
    return (fp == 0) ? 1 : fp; /* Уникаємо нульового відбитка для надійності */
}

/* Ініціалізація та побудова Xor-фільтра */
bool xor_filter_8_build(xor_filter_8_t *filter, const uint64_t *keys, size_t count) {
    if (!filter || !keys || count == 0) return false;

    /* Обчислення довжини сегмента L = ceil(1.23 * count / 3) */
    uint32_t block_len = (uint32_t)((XOR_FILTER_OVERHEAD_FACTOR * (double)count) / 3.0) + 1;
    if (block_len < 32) block_len = 32;
    uint32_t total_slots = 3 * block_len;

    filter->block_length = block_len;
    filter->fingerprints = (uint8_t *)calloc(total_slots, sizeof(uint8_t));
    if (!filter->fingerprints) return false;

    /* Виділення службових структур для лущення */
    uint8_t *hcount = (uint8_t *)malloc(total_slots * sizeof(uint8_t));
    uint64_t *hxor = (uint64_t *)malloc(total_slots * sizeof(uint64_t));
    uint32_t *queue = (uint32_t *)malloc(total_slots * sizeof(uint32_t));
    xor_peel_entry_t *stack = (xor_peel_entry_t *)malloc(count * sizeof(xor_peel_entry_t));

    if (!hcount || !hxor || !queue || !stack) {
        free(filter->fingerprints);
        free(hcount); free(hxor); free(queue); free(stack);
        return false;
    }

    uint64_t seed = 0x8543290134ULL;
    bool success = false;

    for (int attempt = 0; attempt < XOR_FILTER_MAX_ATTEMPTS; ++attempt) {
        seed = xor_hash64(seed + attempt, 0x9e3779b97f4a7c15ULL);
        memset(hcount, 0, total_slots * sizeof(uint8_t));
        memset(hxor, 0, total_slots * sizeof(uint64_t));

        /* Крок 1: Заповнення графів інцидентності */
        for (size_t i = 0; i < count; ++i) {
            uint32_t h0, h1, h2;
            xor_get_positions(keys[i], seed, block_len, &h0, &h1, &h2);

            hcount[h0]++; hxor[h0] ^= keys[i];
            hcount[h1]++; hxor[h1] ^= keys[i];
            hcount[h2]++; hxor[h2] ^= keys[i];
        }

        /* Крок 2: Знаходження початкових вершин степеня 1 */
        uint32_t q_head = 0, q_tail = 0;
        for (uint32_t i = 0; i < total_slots; ++i) {
            if (hcount[i] == 1) {
                queue[q_tail++] = i;
            }
        }

        /* Крок 3: Лущення гіперграфа */
        uint32_t stack_size = 0;
        while (q_head < q_tail) {
            uint32_t slot = queue[q_head++];
            if (hcount[slot] != 1) continue;

            uint64_t key = hxor[slot];
            stack[stack_size].key = key;
            stack[stack_size].index = slot;
            stack_size++;

            uint32_t h[3];
            xor_get_positions(key, seed, block_len, &h[0], &h[1], &h[2]);

            for (int j = 0; j < 3; ++j) {
                uint32_t neighbor = h[j];
                hcount[neighbor]--;
                hxor[neighbor] ^= key;
                if (hcount[neighbor] == 1) {
                    queue[q_tail++] = neighbor;
                }
            }
        }

        /* Якщо всі ключі злущено без виникнення 2-ядра — успіх */
        if (stack_size == count) {
            filter->seed = seed;
            success = true;
            break;
        }
    }

    if (!success) {
        free(filter->fingerprints);
        filter->fingerprints = NULL;
        free(hcount); free(hxor); free(queue); free(stack);
        return false;
    }

    /* Фаза 2: Зворотна підстановка (Back-substitution) */
    memset(filter->fingerprints, 0, total_slots * sizeof(uint8_t));
    while (count > 0) {
        count--;
        uint64_t key = stack[count].key;
        uint32_t slot = stack[count].index;
        uint8_t fp = xor_fingerprint(key, filter->seed);

        uint32_t h[3];
        xor_get_positions(key, filter->seed, block_len, &h[0], &h[1], &h[2]);

        uint8_t other_xor = 0;
        for (int j = 0; j < 3; ++j) {
            if (h[j] != slot) {
                other_xor ^= filter->fingerprints[h[j]];
            }
        }
        filter->fingerprints[slot] = fp ^ other_xor;
    }

    free(hcount); free(hxor); free(queue); free(stack);
    return true;
}

/* Перевірка належності ключа (Lookup) — константний час O(1), branchless */
bool xor_filter_8_contains(const xor_filter_8_t *filter, uint64_t key) {
    if (!filter || !filter->fingerprints) return false;

    uint32_t h0, h1, h2;
    xor_get_positions(key, filter->seed, filter->block_length, &h0, &h1, &h2);
    uint8_t fp = xor_fingerprint(key, filter->seed);

    uint8_t combined = filter->fingerprints[h0] ^
                       filter->fingerprints[h1] ^
                       filter->fingerprints[h2];

    return (combined == fp);
}

/* Звільнення ресурсів */
void xor_filter_8_destroy(xor_filter_8_t *filter) {
    if (filter && filter->fingerprints) {
        free(filter->fingerprints);
        filter->fingerprints = NULL;
        filter->block_length = 0;
    }
}
