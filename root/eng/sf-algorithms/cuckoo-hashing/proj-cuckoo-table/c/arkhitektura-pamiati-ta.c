#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define STASH_CAPACITY 4
#define MAX_DISPLACEMENTS_FACTOR 2

typedef struct {
    uint64_t key;
    uint64_t value;
    bool occupied;
} CuckooEntry;

typedef struct {
    CuckooEntry *t1;
    CuckooEntry *t2;
    CuckooEntry stash[STASH_CAPACITY];
    size_t capacity;      /* розмір кожної з таблиць T1 і T2 */
    size_t size;          /* загальна кількість збережених елементів */
    uint64_t seed1;
    uint64_t seed2;
} CuckooMap;

/* 64-бітне швидке хешування SplitMix64 з домішуванням зерна */
static inline uint64_t hash_splitmix(uint64_t x, uint64_t seed) {
    uint64_t z = (x + seed + 0x9E3779B97F4A7C15ULL);
    z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL;
    z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL;
    return z ^ (z >> 31);
}

static inline size_t index1(const CuckooMap *map, uint64_t key) {
    return (size_t)(hash_splitmix(key, map->seed1) % map->capacity);
}

static inline size_t index2(const CuckooMap *map, uint64_t key) {
    return (size_t)(hash_splitmix(key, map->seed2) % map->capacity);
}

CuckooMap *cuckoo_create(size_t initial_capacity) {
    if (initial_capacity < 8) initial_capacity = 8;
    CuckooMap *map = (CuckooMap *)malloc(sizeof(CuckooMap));
    if (!map) return NULL;

    map->capacity = initial_capacity;
    map->size = 0;
    map->seed1 = 0x8A5CD789ULL;
    map->seed2 = 0xF3B291A4ULL;

    map->t1 = (CuckooEntry *)calloc(map->capacity, sizeof(CuckooEntry));
    map->t2 = (CuckooEntry *)calloc(map->capacity, sizeof(CuckooEntry));
    if (!map->t1 || !map->t2) {
        free(map->t1);
        free(map->t2);
        free(map);
        return NULL;
    }
    memset(map->stash, 0, sizeof(map->stash));
    return map;
}

void cuckoo_destroy(CuckooMap *map) {
    if (!map) return;
    free(map->t1);
    free(map->t2);
    free(map);
}
