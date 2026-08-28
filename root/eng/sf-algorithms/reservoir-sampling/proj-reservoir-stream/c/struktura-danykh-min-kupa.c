#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

/* Вузол пріоритетного резервуара */
typedef struct {
    double key;            /* Логарифмічний ключ r_i = -ln(u_i) / w_i */
    uint64_t item;         /* Збережені дані елемента */
} ares_node_t;

/* Структура зваженого семплера A-Res */
typedef struct {
    ares_node_t *heap;     /* Двійкова макс-купа розміру k */
    size_t capacity;       /* Цільовий розмір вибірки k */
    size_t current_size;   /* Поточна кількість елементів у купі */
    uint64_t total_count;  /* Кількість оброблених елементів */
    uint64_t rng_state;    /* Стан PRNG */
} ares_sampler_t;

static inline void ares_swap(ares_node_t *a, ares_node_t *b) {
    ares_node_t tmp = *a;
    *a = *b;
    *b = tmp;
}

/* Просіювання вгору для макс-купи */
static void ares_sift_up(ares_node_t *heap, size_t idx) {
    while (idx > 0) {
        size_t parent = (idx - 1) / 2;
        /* У макс-купі батьківський елемент має бути більшим або рівним */
        if (heap[idx].key > heap[parent].key) {
            ares_swap(&heap[idx], &heap[parent]);
            idx = parent;
        } else {
            break;
        }
    }
}

/* Просіювання вниз для відновлення інваріанта макс-купи */
static void ares_sift_down(ares_node_t *heap, size_t size, size_t idx) {
    while (2 * idx + 1 < size) {
        size_t left = 2 * idx + 1;
        size_t right = 2 * idx + 2;
        size_t largest = idx;

        if (heap[left].key > heap[largest].key) {
            largest = left;
        }
        if (right < size && heap[right].key > heap[largest].key) {
            largest = right;
        }
        if (largest != idx) {
            ares_swap(&heap[idx], &heap[largest]);
            idx = largest;
        } else {
            break;
        }
    }
}

/* Ініціалізація зваженого семплера */
bool ares_sampler_init(ares_sampler_t *s, size_t capacity, uint64_t seed) {
    if (!s || capacity == 0) return false;
    s->heap = (ares_node_t *)malloc(capacity * sizeof(ares_node_t));
    if (!s->heap) return false;

    s->capacity = capacity;
    s->current_size = 0;
    s->total_count = 0;
    s->rng_state = (seed != 0) ? seed : 0x1f83d9abfb41b7eULL;
    return true;
}

/* Звільнення ресурсів */
void ares_sampler_destroy(ares_sampler_t *s) {
    if (s && s->heap) {
        free(s->heap);
        s->heap = NULL;
    }
}

/* Обробка зваженого елемента */
void ares_sampler_push(ares_sampler_t *s, uint64_t item, double weight) {
    /* Елементи з нульовою чи від'ємною вагою не мають шансу потрапити у вибірку */
    if (weight <= 0.0 || isnan(weight)) return;

    s->total_count++;
    double u = rand_uniform_double(&s->rng_state);
    double key = -log(u) / weight;

    if (s->current_size < s->capacity) {
        /* Купа ще не заповнена: вставка на кінець і просіювання вгору */
        s->heap[s->current_size].key = key;
        s->heap[s->current_size].item = item;
        ares_sift_up(s->heap, s->current_size);
        s->current_size++;
    } else {
        /* Якщо новий ключ менший за максимальний ключ у купі (корінь) */
        if (key < s->heap[0].key) {
            s->heap[0].key = key;
            s->heap[0].item = item;
            ares_sift_down(s->heap, s->current_size, 0);
        }
    }
}
