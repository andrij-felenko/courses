#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

/* Внутрішній стан семплера Algorithm R */
typedef struct {
    uint64_t *buffer;      /* Суцільний масив для зберігання вибірки */
    size_t capacity;       /* Максимальний розмір вибірки k */
    uint64_t total_count;  /* Загальна кількість оброблених елементів n */
    uint64_t rng_state;    /* 64-бітний стан генератора SplitMix64 */
} reservoir_r_t;

/* Генератор псевдовипадкових чисел SplitMix64 (період 2^64) */
static inline uint64_t splitmix64_next(uint64_t *state) {
    uint64_t z = (*state += 0x9e3779b97f4a7c15ULL);
    z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ULL;
    z = (z ^ (z >> 27)) * 0x94d049bb133111ebULL;
    return z ^ (z >> 31);
}

/* Швидка генерація випадкового числа в діапазоні [0, bound - 1] без ділення */
static inline uint64_t fast_rand_range(uint64_t *state, uint64_t bound) {
    uint64_t r = splitmix64_next(state);
    /* Множення 64-біт на 64-біт з отриманням старших 64 біт 128-бітного добутку */
    return (uint64_t)(((__uint128_t)r * (__uint128_t)bound) >> 64);
}

/* Ініціалізація семплера Algorithm R */
bool reservoir_r_init(reservoir_r_t *s, size_t capacity, uint64_t seed) {
    if (!s || capacity == 0) {
        return false;
    }
    s->buffer = (uint64_t *)malloc(capacity * sizeof(uint64_t));
    if (!s->buffer) {
        return false;
    }
    s->capacity = capacity;
    s->total_count = 0;
    s->rng_state = (seed != 0) ? seed : 0x853c49e6748fea9bULL;
    return true;
}

/* Звільнення ресурсів семплера */
void reservoir_r_destroy(reservoir_r_t *s) {
    if (s && s->buffer) {
        free(s->buffer);
        s->buffer = NULL;
    }
}

/* Потокова обробка одного елемента */
void reservoir_r_push(reservoir_r_t *s, uint64_t item) {
    s->total_count++;
    if (s->total_count <= s->capacity) {
        /* Перші k елементів безпосередньо розміщуються в буфері */
        s->buffer[s->total_count - 1] = item;
    } else {
        /* Генерація випадкового індексу в межах [0, total_count - 1] */
        uint64_t j = fast_rand_range(&s->rng_state, s->total_count);
        if (j < s->capacity) {
            /* Заміна елемента в обраному слоті резервуара */
            s->buffer[j] = item;
        }
    }
}

/* Отримання поточної вибірки */
size_t reservoir_r_get_sample(const reservoir_r_t *s, const uint64_t **out_buffer) {
    if (!s || !out_buffer) return 0;
    *out_buffer = s->buffer;
    return (s->total_count < s->capacity) ? (size_t)s->total_count : s->capacity;
}
