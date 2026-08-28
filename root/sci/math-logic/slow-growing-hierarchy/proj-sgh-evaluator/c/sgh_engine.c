/* sgh_engine.h / sgh_engine.c — Обчислювач повільнозростаючої ієрархії на C */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <inttypes.h>

typedef enum {
    ORD_CONST,
    ORD_OMEGA_TERM,
    ORD_SUM,
    ORD_COLLAPSE
} OrdinalKind;

typedef struct OrdinalNode OrdinalNode;

struct OrdinalNode {
    OrdinalKind kind;
    union {
        uint64_t constant;
        struct {
            OrdinalNode *exponent;
            uint64_t coefficient;
        } omega_term;
        struct {
            OrdinalNode **terms;
            size_t count;
            size_t capacity;
        } sum;
        struct {
            OrdinalNode *inner;
        } collapse;
    } as;
};

/* Створення базових вузлів дерева */
OrdinalNode *ord_create_const(uint64_t val) {
    OrdinalNode *n = (OrdinalNode *)malloc(sizeof(OrdinalNode));
    if (!n) return NULL;
    n->kind = ORD_CONST;
    n->as.constant = val;
    return n;
}

OrdinalNode *ord_create_omega_term(OrdinalNode *exponent, uint64_t coeff) {
    OrdinalNode *n = (OrdinalNode *)malloc(sizeof(OrdinalNode));
    if (!n) return NULL;
    n->kind = ORD_OMEGA_TERM;
    n->as.omega_term.exponent = exponent;
    n->as.omega_term.coefficient = coeff;
    return n;
}

OrdinalNode *ord_create_sum(void) {
    OrdinalNode *n = (OrdinalNode *)malloc(sizeof(OrdinalNode));
    if (!n) return NULL;
    n->kind = ORD_SUM;
    n->as.sum.count = 0;
    n->as.sum.capacity = 4;
    n->as.sum.terms = (OrdinalNode **)malloc(sizeof(OrdinalNode *) * n->as.sum.capacity);
    return n;
}

void ord_sum_append(OrdinalNode *sum_node, OrdinalNode *term) {
    if (!sum_node || sum_node->kind != ORD_SUM || !term) return;
    if (sum_node->as.sum.count >= sum_node->as.sum.capacity) {
        sum_node->as.sum.capacity *= 2;
        sum_node->as.sum.terms = (OrdinalNode **)realloc(
            sum_node->as.sum.terms, sizeof(OrdinalNode *) * sum_node->as.sum.capacity);
    }
    sum_node->as.sum.terms[sum_node->as.sum.count++] = term;
}

OrdinalNode *ord_create_collapse(OrdinalNode *inner) {
    OrdinalNode *n = (OrdinalNode *)malloc(sizeof(OrdinalNode));
    if (!n) return NULL;
    n->kind = ORD_COLLAPSE;
    n->as.collapse.inner = inner;
    return n;
}

/* Рекурсивне звільнення динамічної пам'яті */
void ord_free(OrdinalNode *node) {
    if (!node) return;
    switch (node->kind) {
        case ORD_CONST:
            break;
        case ORD_OMEGA_TERM:
            ord_free(node->as.omega_term.exponent);
            break;
        case ORD_SUM:
            for (size_t i = 0; i < node->as.sum.count; ++i) {
                ord_free(node->as.sum.terms[i]);
            }
            free(node->as.sum.terms);
            break;
        case ORD_COLLAPSE:
            ord_free(node->as.collapse.inner);
            break;
    }
    free(node);
}

/* Швидке цілочисельне піднесення до степеня */
static uint64_t ipow(uint64_t base, uint64_t exp) {
    uint64_t res = 1;
    while (exp > 0) {
        if (exp & 1) res *= base;
        base *= base;
        exp >>= 1;
    }
    return res;
}

/* Обчислення G_alpha(n) через алгебраїчний гомоморфізм Кантора */
uint64_t sgh_eval_homomorphism(const OrdinalNode *node, uint64_t n) {
    if (!node) return 0;
    switch (node->kind) {
        case ORD_CONST:
            return node->as.constant;
        case ORD_OMEGA_TERM: {
            uint64_t exp_val = sgh_eval_homomorphism(node->as.omega_term.exponent, n);
            uint64_t base_val = ipow(n, exp_val);
            return base_val * node->as.omega_term.coefficient;
        }
        case ORD_SUM: {
            uint64_t total = 0;
            for (size_t i = 0; i < node->as.sum.count; ++i) {
                total += sgh_eval_homomorphism(node->as.sum.terms[i], n);
            }
            return total;
        }
        case ORD_COLLAPSE: {
            /* Моделювання редукції колапсу: psi(inner)[n] = eval(inner, n) */
            uint64_t inner_val = sgh_eval_homomorphism(node->as.collapse.inner, n);
            return ipow(n, inner_val);
        }
    }
    return 0;
}

/* Демонстрація виконання розрахунків */
int main(void) {
    /* Побудова ординала: alpha = omega^3 * 2 + omega^2 * 5 + 7 */
    OrdinalNode *sum = ord_create_sum();
    ord_sum_append(sum, ord_create_omega_term(ord_create_const(3), 2));
    ord_sum_append(sum, ord_create_omega_term(ord_create_const(2), 5));
    ord_sum_append(sum, ord_create_const(7));

    uint64_t n = 3;
    uint64_t result = sgh_eval_homomorphism(sum, n);
    printf("G_{omega^3 * 2 + omega^2 * 5 + 7}(%" PRIu64 ") = %" PRIu64 "\n", n, result);

    ord_free(sum);
    return 0;
}
