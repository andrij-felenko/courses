#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>
#include <stdlib.h>

#define CMS_DEPTH 4
#define CMS_WIDTH_BITS 14
#define CMS_WIDTH (1U << CMS_WIDTH_BITS)
#define CMS_WIDTH_MASK (CMS_WIDTH - 1)
#define CMS_SAMPLE_WINDOW (CMS_WIDTH * 10)

/* Пакування: два 4-бітних лічильники на один байт uint8_t */
typedef struct {
    uint8_t table[CMS_DEPTH][CMS_WIDTH / 2];
    uint32_t total_additions;
} TinyLfuSketch;

/* Швидкий генератор хешу для рівномірного змішування бітів */
static inline uint64_t hash_string(const char *key, size_t len, uint64_t seed) {
    uint64_t h = seed ^ (len * 0x517cc1b727220a95ULL);
    for (size_t i = 0; i < len; ++i) {
        h ^= (uint8_t)key[i];
        h *= 0x5bd1e9955bd1e995ULL;
        h ^= h >> 47;
    }
    return h;
}

void tiny_lfu_init(TinyLfuSketch *sketch) {
    memset(sketch->table, 0, sizeof(sketch->table));
    sketch->total_additions = 0;
}

/* Зчитування 4-бітного лічильника з комірки */
static inline uint8_t get_counter(const TinyLfuSketch *sketch, int row, uint32_t col) {
    uint8_t byte_val = sketch->table[row][col / 2];
    return (col & 1) ? ((byte_val >> 4) & 0x0F) : (byte_val & 0x0F);
}

/* Інкремент 4-бітного лічильника з насиченням до 15 (0x0F) */
static inline void increment_counter(TinyLfuSketch *sketch, int row, uint32_t col) {
    size_t byte_idx = col / 2;
    uint8_t byte_val = sketch->table[row][byte_idx];
    if (col & 1) {
        uint8_t high = (byte_val >> 4) & 0x0F;
        if (high < 15) {
            high++;
            sketch->table[row][byte_idx] = (byte_val & 0x0F) | (high << 4);
        }
    } else {
        uint8_t low = byte_val & 0x0F;
        if (low < 15) {
            low++;
            sketch->table[row][byte_idx] = (byte_val & 0xF0) | low;
        }
    }
}

/* Старіння (Aging): ділення всіх лічильників навпіл для скидання старих трендів */
static void tiny_lfu_decay(TinyLfuSketch *sketch) {
    for (int r = 0; r < CMS_DEPTH; ++r) {
        for (size_t c = 0; c < CMS_WIDTH / 2; ++c) {
            uint8_t b = sketch->table[r][c];
            uint8_t low = (b & 0x0F) >> 1;
            uint8_t high = ((b >> 4) & 0x0F) >> 1;
            sketch->table[r][c] = (high << 4) | low;
        }
    }
    sketch->total_additions /= 2;
}

/* Фіксація факту звернення до ключа */
void tiny_lfu_record_access(TinyLfuSketch *sketch, const char *key, size_t len) {
    const uint64_t seeds[CMS_DEPTH] = {
        0x100000001b3ULL, 0xcbf29ce484222325ULL,
        0x811c9dc5ULL,    0x9e3779b97f4a7c15ULL
    };

    for (int r = 0; r < CMS_DEPTH; ++r) {
        uint64_t h = hash_string(key, len, seeds[r]);
        uint32_t col = (uint32_t)(h & CMS_WIDTH_MASK);
        increment_counter(sketch, r, col);
    }

    sketch->total_additions++;
    if (sketch->total_additions >= CMS_SAMPLE_WINDOW) {
        tiny_lfu_decay(sketch);
    }
}

/* Оцінка частоти ключа: повертає мінімум по всіх рядках */
uint8_t tiny_lfu_estimate_frequency(const TinyLfuSketch *sketch, const char *key, size_t len) {
    const uint64_t seeds[CMS_DEPTH] = {
        0x100000001b3ULL, 0xcbf29ce484222325ULL,
        0x811c9dc5ULL,    0x9e3779b97f4a7c15ULL
    };

    uint8_t min_freq = 15;
    for (int r = 0; r < CMS_DEPTH; ++r) {
        uint64_t h = hash_string(key, len, seeds[r]);
        uint32_t col = (uint32_t)(h & CMS_WIDTH_MASK);
        uint8_t count = get_counter(sketch, r, col);
        if (count < min_freq) {
            min_freq = count;
        }
    }
    return min_freq;
}

/* Рішення про допуск кандидата замість обраної жертви */
bool tiny_lfu_should_admit(const TinyLfuSketch *sketch,
                           const char *cand_key, size_t cand_len,
                           const char *victim_key, size_t victim_len) {
    uint8_t cand_freq = tiny_lfu_estimate_frequency(sketch, cand_key, cand_len);
    uint8_t victim_freq = tiny_lfu_estimate_frequency(sketch, victim_key, victim_len);
    return cand_freq > victim_freq;
}
