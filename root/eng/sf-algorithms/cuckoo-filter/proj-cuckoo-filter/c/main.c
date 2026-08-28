#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define BUCKET_SIZE 4
#define MAX_KICKS 500
#define EMPTY_SLOT 0

typedef struct {
    uint8_t slots[BUCKET_SIZE];
} CuckooBucket;

typedef struct {
    CuckooBucket *buckets;
    size_t num_buckets;     /* Завжди ступінь двійки */
    size_t bucket_mask;     /* num_buckets - 1 */
    size_t count;           /* Кількість збережених відбитків */
} CuckooFilter;

/* 64-бітний хешер FNV-1a */
static inline uint64_t hash_bytes(const void *data, size_t len) {
    const uint8_t *ptr = (const uint8_t *)data;
    uint64_t hash = 14695981039346656037ULL;
    for (size_t i = 0; i < len; ++i) {
        hash ^= ptr[i];
        hash *= 1099511628211ULL;
    }
    return hash;
}

/* Обчислення 8-бітного відбитка (діапазон 1..255) */
static inline uint8_t get_fingerprint(uint64_t hash) {
    uint8_t fp = (uint8_t)(hash & 0xFF);
    return (fp == EMPTY_SLOT) ? 1 : fp;
}

/* Хеш від самого відбитка для обчислення альтернативного кошика */
static inline size_t hash_fingerprint(uint8_t fp) {
    return (size_t)(fp * 0x9E3779B97F4A7C15ULL);
}

/* Створення фільтра з місткістю не менше target_capacity */
CuckooFilter *cuckoo_create(size_t target_capacity) {
    CuckooFilter *cf = (CuckooFilter *)malloc(sizeof(CuckooFilter));
    if (!cf) return NULL;

    size_t min_buckets = (target_capacity + BUCKET_SIZE - 1) / BUCKET_SIZE;
    size_t num = 16;
    while (num < min_buckets) {
        num <<= 1;
    }

    cf->num_buckets = num;
    cf->bucket_mask = num - 1;
    cf->count = 0;
    cf->buckets = (CuckooBucket *)calloc(num, sizeof(CuckooBucket));
    if (!cf->buckets) {
        free(cf);
        return NULL;
    }
    return cf;
}

void cuckoo_destroy(CuckooFilter *cf) {
    if (cf) {
        free(cf->buckets);
        free(cf);
    }
}

/* Перевірка наявності елемента у фільтрі */
bool cuckoo_contains(const CuckooFilter *cf, const void *data, size_t len) {
    uint64_t h = hash_bytes(data, len);
    uint8_t fp = get_fingerprint(h);
    size_t i1 = (h >> 8) & cf->bucket_mask;
    size_t i2 = (i1 ^ hash_fingerprint(fp)) & cf->bucket_mask;

    const CuckooBucket *b1 = &cf->buckets[i1];
    for (int s = 0; s < BUCKET_SIZE; ++s) {
        if (b1->slots[s] == fp) return true;
    }

    const CuckooBucket *b2 = &cf->buckets[i2];
    for (int s = 0; s < BUCKET_SIZE; ++s) {
        if (b2->slots[s] == fp) return true;
    }

    return false;
}

/* Вставка елемента у фільтр з каскадним витісненням */
bool cuckoo_insert(CuckooFilter *cf, const void *data, size_t len) {
    uint64_t h = hash_bytes(data, len);
    uint8_t fp = get_fingerprint(h);
    size_t i1 = (h >> 8) & cf->bucket_mask;
    size_t i2 = (i1 ^ hash_fingerprint(fp)) & cf->bucket_mask;

    /* 1. Спроба вставити у вільний слот кошика i1 */
    CuckooBucket *b1 = &cf->buckets[i1];
    for (int s = 0; s < BUCKET_SIZE; ++s) {
        if (b1->slots[s] == EMPTY_SLOT) {
            b1->slots[s] = fp;
            cf->count++;
            return true;
        }
    }

    /* 2. Спроба вставити у вільний слот кошика i2 */
    CuckooBucket *b2 = &cf->buckets[i2];
    for (int s = 0; s < BUCKET_SIZE; ++s) {
        if (b2->slots[s] == EMPTY_SLOT) {
            b2->slots[s] = fp;
            cf->count++;
            return true;
        }
    }

    /* 3. Обидва кошики повні: ініціюємо каскадне витіснення */
    size_t curr_i = (rand() & 1) ? i1 : i2;
    uint8_t curr_fp = fp;

    for (int kick = 0; kick < MAX_KICKS; ++kick) {
        int slot_idx = rand() % BUCKET_SIZE;
        uint8_t evicted_fp = cf->buckets[curr_i].slots[slot_idx];
        cf->buckets[curr_i].slots[slot_idx] = curr_fp;

        curr_i = (curr_i ^ hash_fingerprint(evicted_fp)) & cf->bucket_mask;
        curr_fp = evicted_fp;

        CuckooBucket *target = &cf->buckets[curr_i];
        for (int s = 0; s < BUCKET_SIZE; ++s) {
            if (target->slots[s] == EMPTY_SLOT) {
                target->slots[s] = curr_fp;
                cf->count++;
                return true;
            }
        }
    }

    return false; /* Переповнення */
}

/* Видалення одного екземпляра відбитка */
bool cuckoo_delete(CuckooFilter *cf, const void *data, size_t len) {
    uint64_t h = hash_bytes(data, len);
    uint8_t fp = get_fingerprint(h);
    size_t i1 = (h >> 8) & cf->bucket_mask;
    size_t i2 = (i1 ^ hash_fingerprint(fp)) & cf->bucket_mask;

    CuckooBucket *b1 = &cf->buckets[i1];
    for (int s = 0; s < BUCKET_SIZE; ++s) {
        if (b1->slots[s] == fp) {
            b1->slots[s] = EMPTY_SLOT;
            cf->count--;
            return true;
        }
    }

    CuckooBucket *b2 = &cf->buckets[i2];
    for (int s = 0; s < BUCKET_SIZE; ++s) {
        if (b2->slots[s] == fp) {
            b2->slots[s] = EMPTY_SLOT;
            cf->count--;
            return true;
        }
    }

    return false;
}

double cuckoo_load_factor(const CuckooFilter *cf) {
    return (double)cf->count / (double)(cf->num_buckets * BUCKET_SIZE);
}
