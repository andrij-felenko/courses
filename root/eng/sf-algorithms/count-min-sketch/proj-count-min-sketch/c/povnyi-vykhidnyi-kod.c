#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
#include <stdbool.h>

/* Попарно незалежні параметри хешування для a * x + b mod p */
typedef struct {
    uint64_t a;
    uint64_t b;
} cm_hash_param_t;

typedef struct {
    uint32_t depth;            /* Кількість рядків d = ceil(ln(1 / delta)) */
    uint32_t width;            /* Кількість стовпців w = ceil(e / epsilon) */
    uint64_t total_count;      /* Загальний обсяг обробленого потоку (L1-норма) */
    uint32_t *table;           /* Плаский масив лічильників розміром depth * width */
    cm_hash_param_t *params;   /* Параметри хеш-функцій для кожного рядка */
} cm_sketch_t;

/* Обчислення 64-бітного хешу для довільного буфера байтів (MurmurHash3-подібний міксер) */
static uint64_t cm_hash_bytes(const void *key, size_t len, uint64_t seed) {
    const uint8_t *data = (const uint8_t *)key;
    uint64_t h = seed ^ (len * 0xc6a4a7935bd1e995ULL);
    
    while (len >= 8) {
        uint64_t k;
        memcpy(&k, data, sizeof(uint64_t));
        k *= 0xc6a4a7935bd1e995ULL;
        k ^= k >> 47;
        k *= 0xc6a4a7935bd1e995ULL;
        h ^= k;
        h *= 0xc6a4a7935bd1e995ULL;
        data += 8;
        len -= 8;
    }
    
    if (len > 0) {
        uint64_t tail = 0;
        memcpy(&tail, data, len);
        h ^= tail;
        h *= 0xc6a4a7935bd1e995ULL;
    }
    
    h ^= h >> 47;
    h *= 0xc6a4a7935bd1e995ULL;
    h ^= h >> 47;
    return h;
}

/* Ініціалізація Count-Min Sketch за бажаними параметрами точності epsilon та delta */
cm_sketch_t *cm_create(double epsilon, double delta) {
    if (epsilon <= 0.0 || delta <= 0.0 || delta >= 1.0) {
        return NULL;
    }
    
    cm_sketch_t *sketch = (cm_sketch_t *)malloc(sizeof(cm_sketch_t));
    if (!sketch) return NULL;
    
    sketch->width = (uint32_t)ceil(exp(1.0) / epsilon);
    sketch->depth = (uint32_t)ceil(log(1.0 / delta));
    sketch->total_count = 0;
    
    size_t total_cells = (size_t)sketch->depth * sketch->width;
    sketch->table = (uint32_t *)calloc(total_cells, sizeof(uint32_t));
    if (!sketch->table) {
        free(sketch);
        return NULL;
    }
    
    sketch->params = (cm_hash_param_t *)malloc(sketch->depth * sizeof(cm_hash_param_t));
    if (!sketch->params) {
        free(sketch->table);
        free(sketch);
        return NULL;
    }
    
    /* Генерація випадкових параметрів для хеш-рядків */
    for (uint32_t i = 0; i < sketch->depth; ++i) {
        sketch->params[i].a = ((uint64_t)rand() << 32) | rand() | 1ULL;
        sketch->params[i].b = ((uint64_t)rand() << 32) | rand();
    }
    
    return sketch;
}

void cm_destroy(cm_sketch_t *sketch) {
    if (!sketch) return;
    free(sketch->table);
    free(sketch->params);
    free(sketch);
}

/* Обчислення індексу стовпця для рядка row */
static inline uint32_t cm_get_col(const cm_sketch_t *sketch, uint32_t row, const void *key, size_t len) {
    uint64_t raw_hash = cm_hash_bytes(key, len, sketch->params[row].b);
    uint64_t mapped = (raw_hash ^ sketch->params[row].a);
    return (uint32_t)(mapped % sketch->width);
}

/* Стандартне оновлення: збільшення лічильника в кожному рядку */
void cm_update(cm_sketch_t *sketch, const void *key, size_t len, uint32_t count) {
    if (!sketch || !key || count == 0) return;
    
    for (uint32_t r = 0; r < sketch->depth; ++r) {
        uint32_t col = cm_get_col(sketch, r, key, len);
        sketch->table[r * sketch->width + col] += count;
    }
    sketch->total_count += count;
}

/* Консервативне оновлення: інкремент лише тих лічильників, що досягають нового мінімуму */
void cm_update_conservative(cm_sketch_t *sketch, const void *key, size_t len, uint32_t count) {
    if (!sketch || !key || count == 0) return;
    
    uint32_t min_val = UINT32_MAX;
    uint32_t *cols = (uint32_t *)malloc(sketch->depth * sizeof(uint32_t));
    if (!cols) return;
    
    for (uint32_t r = 0; r < sketch->depth; ++r) {
        cols[r] = cm_get_col(sketch, r, key, len);
        uint32_t val = sketch->table[r * sketch->width + cols[r]];
        if (val < min_val) min_val = val;
    }
    
    uint32_t new_min = min_val + count;
    for (uint32_t r = 0; r < sketch->depth; ++r) {
        uint32_t idx = r * sketch->width + cols[r];
        if (sketch->table[idx] < new_min) {
            sketch->table[idx] = new_min;
        }
    }
    
    sketch->total_count += count;
    free(cols);
}

/* Точковий запит частоти: взяття мінімуму по всіх рядках */
uint32_t cm_estimate(const cm_sketch_t *sketch, const void *key, size_t len) {
    if (!sketch || !key) return 0;
    
    uint32_t min_val = UINT32_MAX;
    for (uint32_t r = 0; r < sketch->depth; ++r) {
        uint32_t col = cm_get_col(sketch, r, key, len);
        uint32_t val = sketch->table[r * sketch->width + col];
        if (val < min_val) min_val = val;
    }
    return min_val;
}

/* Поелементне об'єднання двох ескізів (A = A + B) */
bool cm_merge(cm_sketch_t *dest, const cm_sketch_t *src) {
    if (!dest || !src || dest->depth != src->depth || dest->width != src->width) {
        return false;
    }
    
    size_t total_cells = (size_t)dest->depth * dest->width;
    for (size_t i = 0; i < total_cells; ++i) {
        dest->table[i] += src->table[i];
    }
    dest->total_count += src->total_count;
    return true;
}
