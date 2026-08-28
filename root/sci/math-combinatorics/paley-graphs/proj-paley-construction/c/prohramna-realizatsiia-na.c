#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

/* Структура для компактного представлення графа Пейлі через бітову матрицю */
typedef struct {
    uint32_t p;             /* Порядок поля (кількість вершин) */
    uint32_t words_per_row; /* Кількість 64-бітних слів на один рядок */
    uint64_t *adj;          /* Бітова матриця суміжності (p * words_per_row) */
    bool *is_square;        /* Таблиця квадратичних лишків розміру p */
} PaleyGraphC;

/* Ініціалізація та побудова графа Пейлі */
PaleyGraphC* paley_create(uint32_t p) {
    if (p < 5 || (p % 4) != 1) {
        return NULL; /* Граф Пейлі визначено лише для p = 1 (mod 4) */
    }

    PaleyGraphC *g = (PaleyGraphC*)malloc(sizeof(PaleyGraphC));
    if (!g) return NULL;

    g->p = p;
    g->words_per_row = (p + 63) / 64;
    g->adj = (uint64_t*)calloc((size_t)p * g->words_per_row, sizeof(uint64_t));
    g->is_square = (bool*)calloc(p, sizeof(bool));

    if (!g->adj || !g->is_square) {
        free(g->adj);
        free(g->is_square);
        free(g);
        return NULL;
    }

    /* 1. Попередня генерація квадратичних лишків: x^2 mod p */
    for (uint32_t x = 1; x <= p / 2; ++x) {
        uint32_t sq = (uint32_t)(((uint64_t)x * x) % p);
        g->is_square[sq] = true;
    }

    /* 2. Заповнення бітової матриці суміжності */
    for (uint32_t u = 0; u < p; ++u) {
        for (uint32_t v = 0; v < p; ++v) {
            if (u == v) continue;
            uint32_t diff = (u >= v) ? (u - v) : (u + p - v);
            if (g->is_square[diff]) {
                uint32_t word_idx = u * g->words_per_row + (v / 64);
                g->adj[word_idx] |= ((uint64_t)1 << (v % 64));
            }
        }
    }

    return g;
}

void paley_free(PaleyGraphC *g) {
    if (!g) return;
    free(g->adj);
    free(g->is_square);
    free(g);
}

/* Перевірка суміжності двох вершин */
bool paley_is_adjacent(const PaleyGraphC *g, uint32_t u, uint32_t v) {
    if (u >= g->p || v >= g->p || u == v) return false;
    uint32_t word_idx = u * g->words_per_row + (v / 64);
    return (g->adj[word_idx] & ((uint64_t)1 << (v % 64))) != 0;
}

/* Підрахунок спільних сусідів через побітове AND та popcount */
uint32_t paley_common_neighbours(const PaleyGraphC *g, uint32_t u, uint32_t v) {
    if (u >= g->p || v >= g->p) return 0;
    uint32_t count = 0;
    uint32_t offset_u = u * g->words_per_row;
    uint32_t offset_v = v * g->words_per_row;

    for (uint32_t w = 0; w < g->words_per_row; ++w) {
        uint64_t mask = g->adj[offset_u + w] & g->adj[offset_v + w];
        count += (uint32_t)__builtin_popcountll(mask);
    }
    return count;
}

/* Повна верифікація параметрів srg(p, k, lambda, mu) */
bool paley_verify_srg(const PaleyGraphC *g, uint32_t *out_k, uint32_t *out_lambda, uint32_t *out_mu) {
    uint32_t expected_k = (g->p - 1) / 2;
    uint32_t expected_lambda = (g->p - 5) / 4;
    uint32_t expected_mu = (g->p - 1) / 4;

    if (out_k) *out_k = expected_k;
    if (out_lambda) *out_lambda = expected_lambda;
    if (out_mu) *out_mu = expected_mu;

    /* 1. Перевірка регулярності степенів */
    for (uint32_t u = 0; u < g->p; ++u) {
        uint32_t deg = 0;
        uint32_t offset = u * g->words_per_row;
        for (uint32_t w = 0; w < g->words_per_row; ++w) {
            deg += (uint32_t)__builtin_popcountll(g->adj[offset + w]);
        }
        if (deg != expected_k) return false;
    }

    /* 2. Перевірка кількості спільних сусідів для всіх пар */
    for (uint32_t u = 0; u < g->p; ++u) {
        for (uint32_t v = u + 1; v < g->p; ++v) {
            uint32_t common = paley_common_neighbours(g, u, v);
            bool adj = paley_is_adjacent(g, u, v);
            if (adj && common != expected_lambda) return false;
            if (!adj && common != expected_mu) return false;
        }
    }

    return true;
}
