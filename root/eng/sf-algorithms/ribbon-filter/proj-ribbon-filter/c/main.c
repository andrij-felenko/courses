#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

#define RIBBON_WIDTH 64
#define RIBBON_OVERHEAD_PERCENT 5
#define MAX_SEED_RETRIES 10

/* Швидкий некриптографічний 64-бітний хешувальний міксер (SplitMix64) */
static inline uint64_t ribbon_hash64(uint64_t x, uint64_t seed) {
    uint64_t z = x + seed + 0x9e3779b97f4a7c15ULL;
    z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ULL;
    z = (z ^ (z >> 27)) * 0x94d049bb133111ebULL;
    return z ^ (z >> 31);
}

/* Структура тимчасового опорного рядка для розв'язання системи Гаусса */
typedef struct {
    uint64_t mask;
    uint8_t target;
    bool occupied;
} RibbonPivot;

/* Основна структура стрічкового фільтра */
typedef struct {
    uint8_t *slots;          /* Масив розв'язаних слотів B */
    size_t num_slots;        /* Загальна кількість слотів M */
    size_t num_keys;         /* Кількість збережених ключів N */
    uint64_t seed;           /* Поточний seed хешування */
} RibbonFilter;

/* Генерація параметрів рівняння для заданого ключа */
static inline void ribbon_key_params(uint64_t key, uint64_t seed, size_t num_slots,
                                     size_t *out_start, uint64_t *out_mask, uint8_t *out_target) {
    uint64_t h1 = ribbon_hash64(key, seed);
    uint64_t h2 = ribbon_hash64(key, seed ^ 0x517cc1b727220a95ULL);
    
    /* Обчислення початкового зміщення p ∈ [0, num_slots - RIBBON_WIDTH] */
    size_t max_start = (num_slots >= RIBBON_WIDTH) ? (num_slots - RIBBON_WIDTH) : 0;
    *out_start = (size_t)(((__uint128_t)h1 * (max_start + 1)) >> 64);
    
    /* Формування стрічкової маски: гарантуємо хоча б одну '1' */
    uint64_t mask = h2;
    if (mask == 0) mask = 1ULL;
    *out_mask = mask;
    
    /* Обчислення цільового 8-бітного відбитка f(x) (виключаємо 0 для надійності) */
    uint8_t target = (uint8_t)((h1 >> 32) ^ (h2 >> 32));
    *out_target = (target == 0) ? 1 : target;
}

/* Ініціалізація та побудова стрічкового фільтра за масивом ключів */
bool ribbon_filter_build(RibbonFilter *filter, const uint64_t *keys, size_t num_keys) {
    if (num_keys == 0) return false;
    
    /* Кількість слотів M = N * (1 + overhead) */
    size_t num_slots = (num_keys * (100 + RIBBON_OVERHEAD_PERCENT)) / 100;
    if (num_slots < RIBBON_WIDTH) num_slots = RIBBON_WIDTH;
    
    filter->num_keys = num_keys;
    filter->num_slots = num_slots;
    filter->slots = (uint8_t *)calloc(num_slots, sizeof(uint8_t));
    if (!filter->slots) return false;
    
    RibbonPivot *pivots = (RibbonPivot *)calloc(num_slots, sizeof(RibbonPivot));
    if (!pivots) {
        free(filter->slots);
        filter->slots = NULL;
        return false;
    }
    
    for (uint64_t retry = 0; retry < MAX_SEED_RETRIES; ++retry) {
        uint64_t seed = 0x12345678ULL + retry * 0x9e3779b9ULL;
        memset(pivots, 0, num_slots * sizeof(RibbonPivot));
        bool success = true;
        
        /* Прямий хід: інкрементне виключення Гаусса для кожного ключа */
        for (size_t i = 0; i < num_keys; ++i) {
            size_t start_pos;
            uint64_t mask;
            uint8_t target;
            ribbon_key_params(keys[i], seed, num_slots, &start_pos, &mask, &target);
            
            size_t col = start_pos;
            while (mask != 0) {
                /* Знаходимо індекс молодшого одиничного біта */
                int offset = __builtin_ctzll(mask);
                col += (size_t)offset;
                mask >>= offset;
                
                if (col >= num_slots) {
                    success = false;
                    break;
                }
                
                if (!pivots[col].occupied) {
                    /* Слот вільний — фіксуємо рядок як опорний */
                    pivots[col].mask = mask;
                    pivots[col].target = target;
                    pivots[col].occupied = true;
                    break;
                }
                
                /* Колізія: виключаємо провідну одиницю через XOR */
                mask ^= pivots[col].mask;
                target ^= pivots[col].target;
            }
            
            /* Якщо маска обнулилася, але відбиток не сходиться — система несумісна */
            if (mask == 0 && target != 0) {
                success = false;
                break;
            }
        }
        
        if (success) {
            /* Зворотний хід: обчислення остаточних значень слотів B[0..M-1] */
            memset(filter->slots, 0, num_slots * sizeof(uint8_t));
            for (size_t i = num_slots; i-- > 0;) {
                if (pivots[i].occupied) {
                    uint8_t accum = 0;
                    uint64_t mask = pivots[i].mask;
                    
                    /* Сумуємо відомі змінні з вікна [i+1, i+63] */
                    for (size_t bit = 1; bit < RIBBON_WIDTH && (i + bit) < num_slots; ++bit) {
                        if ((mask >> bit) & 1ULL) {
                            accum ^= filter->slots[i + bit];
                        }
                    }
                    filter->slots[i] = pivots[i].target ^ accum;
                } else {
                    filter->slots[i] = 0;
                }
            }
            
            filter->seed = seed;
            free(pivots);
            return true;
        }
    }
    
    free(pivots);
    free(filter->slots);
    filter->slots = NULL;
    return false;
}

/* Перевірка належності ключа у фільтрі (Query) */
bool ribbon_filter_contains(const RibbonFilter *filter, uint64_t key) {
    if (!filter || !filter->slots) return false;
    
    size_t start_pos;
    uint64_t mask;
    uint8_t expected_target;
    ribbon_key_params(key, filter->seed, filter->num_slots, &start_pos, &mask, &expected_target);
    
    /* Обчислення скалярного добутку маски та слотів над GF(2)^8 */
    uint8_t result = 0;
    for (size_t bit = 0; bit < RIBBON_WIDTH && (start_pos + bit) < filter->num_slots; ++bit) {
        if ((mask >> bit) & 1ULL) {
            result ^= filter->slots[start_pos + bit];
        }
    }
    
    return result == expected_target;
}

/* Звільнення ресурсів фільтра */
void ribbon_filter_destroy(RibbonFilter *filter) {
    if (filter && filter->slots) {
        free(filter->slots);
        filter->slots = NULL;
        filter->num_slots = 0;
        filter->num_keys = 0;
    }
}
