#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

/* Стан семплера зі стрибками Algorithm L */
typedef struct {
    uint64_t *buffer;      /* Буфер резервуара */
    size_t capacity;       /* Місткість k */
    uint64_t total_count;  /* Загальна кількість елементів потоку */
    uint64_t skip_count;   /* Кількість елементів, які слід пропустити */
    double W;              /* Ваговий коефіцієнт інтервалу Віттера */
    uint64_t rng_state;    /* Стан PRNG SplitMix64 */
} reservoir_l_t;

/* Генерація псевдовипадкового дійсного числа з інтервалу (0, 1) */
static inline double rand_uniform_double(uint64_t *state) {
    uint64_t r = splitmix64_next(state);
    /* Використання 53 біт мантиси стандарту IEEE 754 */
    return ((r >> 11) * (1.0 / 9007199254740992.0)) + 1e-16;
}

/* Обчислення довжини наступного стрибка S */
static inline uint64_t compute_skip_distance(double W, uint64_t *state) {
    double u = rand_uniform_double(state);
    return (uint64_t)(log(u) / log(1.0 - W));
}

/* Ініціалізація семплера Algorithm L */
bool reservoir_l_init(reservoir_l_t *s, size_t capacity, uint64_t seed) {
    if (!s || capacity == 0) return false;
    s->buffer = (uint64_t *)malloc(capacity * sizeof(uint64_t));
    if (!s->buffer) return false;

    s->capacity = capacity;
    s->total_count = 0;
    s->skip_count = 0;
    s->W = 1.0;
    s->rng_state = (seed != 0) ? seed : 0x4d595df4d0f33173ULL;
    return true;
}

/* Звільнення ресурсів */
void reservoir_l_destroy(reservoir_l_t *s) {
    if (s && s->buffer) {
        free(s->buffer);
        s->buffer = NULL;
    }
}

/* Потокова обробка елемента в Algorithm L */
void reservoir_l_push(reservoir_l_t *s, uint64_t item) {
    s->total_count++;
    if (s->total_count <= s->capacity) {
        s->buffer[s->total_count - 1] = item;
        if (s->total_count == s->capacity) {
            /* Буфер заповнено: розрахунок початкової ваги W та першого стрибка */
            double u = rand_uniform_double(&s->rng_state);
            s->W = exp(log(u) / (double)s->capacity);
            s->skip_count = compute_skip_distance(s->W, &s->rng_state);
        }
    } else {
        if (s->skip_count == 0) {
            /* Інтервал пропуску завершився: поточний елемент потрапляє у вибірку */
            uint64_t slot = fast_rand_range(&s->rng_state, s->capacity);
            s->buffer[slot] = item;

            /* Оновлення кумулятивної ваги W та розрахунок нового інтервалу стрибка */
            double u = rand_uniform_double(&s->rng_state);
            s->W = s->W * exp(log(u) / (double)s->capacity);
            s->skip_count = compute_skip_distance(s->W, &s->rng_state);
        } else {
            /* Швидкісний пропуск: декремент без жодних математичних операцій */
            s->skip_count--;
        }
    }
}

/* Пакетний пропуск масиву елементів (векторна оптимізація) */
void reservoir_l_push_batch(reservoir_l_t *s, const uint64_t *items, size_t count) {
    size_t idx = 0;
    while (idx < count) {
        if (s->total_count < s->capacity) {
            reservoir_l_push(s, items[idx++]);
        } else if (s->skip_count >= (count - idx)) {
            /* Увесь залишок пакета гарантовано пропускається одним кроком */
            size_t remaining = count - idx;
            s->total_count += remaining;
            s->skip_count -= remaining;
            break;
        } else {
            /* Пропуск до найближчої точки заміни */
            idx += s->skip_count;
            s->total_count += s->skip_count;
            s->skip_count = 0;
            if (idx < count) {
                reservoir_l_push(s, items[idx++]);
            }
        }
    }
}
