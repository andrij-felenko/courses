#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

typedef enum {
    ORD_ZERO,
    ORD_FINITE,
    ORD_TERM
} OrdinalKind;

typedef struct OrdinalNode {
    OrdinalKind kind;
    uint64_t finite_val;
    struct OrdinalNode* exponent;
    uint64_t coeff;
    struct OrdinalNode* tail;
} OrdinalNode;

typedef struct {
    uint64_t total_steps;
    uint64_t max_depth;
    uint64_t current_depth;
    bool limit_exceeded;
} EvaluationStats;

/* Конструктори вузлів дерева ординалів */
OrdinalNode* ord_create_zero(void) {
    OrdinalNode* node = (OrdinalNode*)calloc(1, sizeof(OrdinalNode));
    node->kind = ORD_ZERO;
    return node;
}

OrdinalNode* ord_create_finite(uint64_t val) {
    if (val == 0) return ord_create_zero();
    OrdinalNode* node = (OrdinalNode*)calloc(1, sizeof(OrdinalNode));
    node->kind = ORD_FINITE;
    node->finite_val = val;
    return node;
}

OrdinalNode* ord_create_term(OrdinalNode* exp, uint64_t coeff, OrdinalNode* tail) {
    OrdinalNode* node = (OrdinalNode*)calloc(1, sizeof(OrdinalNode));
    node->kind = ORD_TERM;
    node->exponent = exp;
    node->coeff = coeff;
    node->tail = tail;
    return node;
}

void ord_free(OrdinalNode* node) {
    if (!node) return;
    ord_free(node->exponent);
    ord_free(node->tail);
    free(node);
}

/* Перевірка чи є ординал граничним */
bool ord_is_limit(const OrdinalNode* node) {
    if (!node || node->kind == ORD_ZERO || node->kind == ORD_FINITE) return false;
    if (node->tail != NULL && node->tail->kind != ORD_ZERO) {
        return ord_is_limit(node->tail);
    }
    return (node->exponent->kind != ORD_ZERO);
}

/* Обчислення фундаментальної послідовності λ[n] */
OrdinalNode* ord_fundamental_sequence(const OrdinalNode* lambda, uint64_t n) {
    if (!lambda || lambda->kind != ORD_TERM) return ord_create_zero();

    if (lambda->tail != NULL && lambda->tail->kind != ORD_ZERO) {
        /* α = γ + tail -> α[n] = γ + tail[n] */
        return ord_create_term(
            lambda->exponent,
            lambda->coeff,
            ord_fundamental_sequence(lambda->tail, n)
        );
    }

    /* Випадок термового додатка: ω^exp * coeff */
    if (lambda->coeff > 1) {
        /* ω^exp * c -> ω^exp * (c - 1) + (ω^exp)[n] */
        OrdinalNode* single_term = ord_create_term(lambda->exponent, 1, NULL);
        OrdinalNode* reduced = ord_fundamental_sequence(single_term, n);
        ord_free(single_term);
        return ord_create_term(lambda->exponent, lambda->coeff - 1, reduced);
    }

    /* λ = ω^exp */
    if (lambda->exponent->kind == ORD_FINITE && lambda->exponent->finite_val == 1) {
        /* ω^1 [n] = n */
        return ord_create_finite(n);
    }

    if (!ord_is_limit(lambda->exponent)) {
        /* exp = β + 1 -> (ω^(β+1))[n] = ω^β * n */
        OrdinalNode* exp_minus_1 = ord_fundamental_sequence(lambda->exponent, 1);
        OrdinalNode* res = ord_create_term(exp_minus_1, n, NULL);
        return res;
    } else {
        /* exp є граничним -> (ω^λ)[n] = ω^(λ[n]) */
        OrdinalNode* exp_fund = ord_fundamental_sequence(lambda->exponent, n);
        return ord_create_term(exp_fund, 1, NULL);
    }
}

/* Обчислення F_α(n) */
uint64_t fgh_eval(OrdinalNode* alpha, uint64_t n, EvaluationStats* stats, uint64_t max_steps) {
    stats->total_steps++;
    stats->current_depth++;
    if (stats->current_depth > stats->max_depth) {
        stats->max_depth = stats->current_depth;
    }

    if (stats->total_steps > max_steps) {
        stats->limit_exceeded = true;
        stats->current_depth--;
        return n;
    }

    if (!alpha || alpha->kind == ORD_ZERO) {
        /* F_0(n) = n + 1 */
        stats->current_depth--;
        return n + 1;
    }

    if (alpha->kind == ORD_FINITE) {
        if (alpha->finite_val == 0) {
            stats->current_depth--;
            return n + 1;
        }
        /* F_k(n) через ітерації */
        OrdinalNode* prev = ord_create_finite(alpha->finite_val - 1);
        uint64_t acc = n;
        for (uint64_t i = 0; i < n; i++) {
            acc = fgh_eval(prev, acc, stats, max_steps);
            if (stats->limit_exceeded) break;
        }
        ord_free(prev);
        stats->current_depth--;
        return acc;
    }

    /* Граничний чи вищий трансфінітний крок */
    OrdinalNode* fund = ord_fundamental_sequence(alpha, n);
    uint64_t res = fgh_eval(fund, n, stats, max_steps);
    ord_free(fund);
    stats->current_depth--;
    return res;
}

int main(void) {
    EvaluationStats stats = {0};
    /* Створення ординала ω */
    OrdinalNode* omega = ord_create_term(ord_create_finite(1), 1, NULL);

    printf("--- Двигун обчислення FGH (C) ---\n");
    uint64_t val = fgh_eval(omega, 3, &stats, 1000000);
    printf("F_omega(3) = %glu (Кроків: %glu, Макс. глибина: %glu)\n", 
           val, stats.total_steps, stats.max_depth);

    ord_free(omega);
    return 0;
}
