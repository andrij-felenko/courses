#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

/* Типи вузлів AST для елементарних функцій Кальмара */
typedef enum {
    NODE_CONST,
    NODE_VAR,
    NODE_ADD,
    NODE_SUB,
    NODE_MUL,
    NODE_DIV,
    NODE_EXP,
    NODE_SUM,
    NODE_PROD,
    NODE_SEARCH
} NodeType;

typedef struct ExprNode ExprNode;

struct ExprNode {
    NodeType type;
    uint64_t val;               /* Для констант */
    size_t var_idx;             /* Для змінних та параметрів циклу */
    ExprNode* left;             /* Лівий операнд або вираз межі */
    ExprNode* right;            /* Правий операнд або тіло циклу */
};

/* Створення вузлів AST */
ExprNode* make_const(uint64_t v) {
    ExprNode* n = (ExprNode*)calloc(1, sizeof(ExprNode));
    n->type = NODE_CONST;
    n->val = v;
    return n;
}

ExprNode* make_var(size_t idx) {
    ExprNode* n = (ExprNode*)calloc(1, sizeof(ExprNode));
    n->type = NODE_VAR;
    n->var_idx = idx;
    return n;
}

ExprNode* make_binop(NodeType type, ExprNode* l, ExprNode* r) {
    ExprNode* n = (ExprNode*)calloc(1, sizeof(ExprNode));
    n->type = type;
    n->left = l;
    n->right = r;
    return n;
}

ExprNode* make_bounded(NodeType type, size_t var_idx, ExprNode* bound, ExprNode* body) {
    ExprNode* n = (ExprNode*)calloc(1, sizeof(ExprNode));
    n->type = type;
    n->var_idx = var_idx;
    n->left = bound;
    n->right = body;
    return n;
}

void free_tree(ExprNode* n) {
    if (!n) return;
    free_tree(n->left);
    free_tree(n->right);
    free(n);
}

/* Статичний розрахунок верхньої межі висоти експоненціальної вежі */
size_t compute_tower_height(const ExprNode* n) {
    if (!n) return 0;
    switch (n->type) {
        case NODE_CONST:
        case NODE_VAR:
            return 0;
        case NODE_ADD:
        case NODE_SUB:
        case NODE_MUL:
        case NODE_DIV: {
            size_t hl = compute_tower_height(n->left);
            size_t hr = compute_tower_height(n->right);
            return (hl > hr) ? hl : hr;
        }
        case NODE_EXP: {
            size_t hl = compute_tower_height(n->left);
            size_t hr = compute_tower_height(n->right);
            size_t hm = (hl > hr) ? hl : hr;
            return hm + 1;
        }
        case NODE_SUM:
        case NODE_PROD: {
            size_t hb = compute_tower_height(n->right);
            return hb + 1;
        }
        case NODE_SEARCH:
            return compute_tower_height(n->left);
    }
    return 0;
}

/* Безпечне цілочисельне піднесення до степеня */
static uint64_t safe_pow(uint64_t base, uint64_t exp) {
    if (exp == 0) return 1;
    if (base == 0) return 0;
    uint64_t res = 1;
    uint64_t b = base;
    while (exp > 0) {
        if (exp & 1) res *= b;
        b *= b;
        exp >>= 1;
    }
    return res;
}

/* Динамічний обчислювач виразів Кальмара */
uint64_t eval_expr(const ExprNode* n, uint64_t* env, size_t env_len) {
    if (!n) return 0;
    switch (n->type) {
        case NODE_CONST:
            return n->val;
        case NODE_VAR:
            if (n->var_idx < env_len) return env[n->var_idx];
            return 0;
        case NODE_ADD:
            return eval_expr(n->left, env, env_len) + eval_expr(n->right, env, env_len);
        case NODE_SUB: {
            uint64_t l = eval_expr(n->left, env, env_len);
            uint64_t r = eval_expr(n->right, env, env_len);
            return (l >= r) ? (l - r) : 0; /* Зрізане віднімання */
        }
        case NODE_MUL:
            return eval_expr(n->left, env, env_len) * eval_expr(n->right, env, env_len);
        case NODE_DIV: {
            uint64_t r = eval_expr(n->right, env, env_len);
            if (r == 0) return 0; /* За визначенням Кальмара Div(x, 0) = 0 */
            return eval_expr(n->left, env, env_len) / r;
        }
        case NODE_EXP: {
            uint64_t b = eval_expr(n->left, env, env_len);
            uint64_t e = eval_expr(n->right, env, env_len);
            return safe_pow(b, e);
        }
        case NODE_SUM: {
            uint64_t bound = eval_expr(n->left, env, env_len);
            uint64_t sum = 0;
            for (uint64_t z = 0; z <= bound; ++z) {
                if (n->var_idx < env_len) env[n->var_idx] = z;
                sum += eval_expr(n->right, env, env_len);
            }
            return sum;
        }
        case NODE_PROD: {
            uint64_t bound = eval_expr(n->left, env, env_len);
            uint64_t prod = 1;
            for (uint64_t z = 0; z <= bound; ++z) {
                if (n->var_idx < env_len) env[n->var_idx] = z;
                prod *= eval_expr(n->right, env, env_len);
            }
            return prod;
        }
        case NODE_SEARCH: {
            uint64_t bound = eval_expr(n->left, env, env_len);
            for (uint64_t z = 0; z <= bound; ++z) {
                if (n->var_idx < env_len) env[n->var_idx] = z;
                if (eval_expr(n->right, env, env_len) == 1) {
                    return z; /* Знайдено найменший задовольняючий індекс */
                }
            }
            return bound; /* Якщо розв'язку немає, повертаємо саму межу */
        }
    }
    return 0;
}

int main(void) {
    uint64_t env[8] = {0};

    /* Приклад 1. Факторіал: n! = Prod_{z < n} (z + 1) = Prod_{z <= (n ∸ 1)} (z + 1) */
    /* env[0] = n, env[1] = z */
    ExprNode* n_sub_1 = make_binop(NODE_SUB, make_var(0), make_const(1));
    ExprNode* z_plus_1 = make_binop(NODE_ADD, make_var(1), make_const(1));
    ExprNode* fact_expr = make_bounded(NODE_PROD, 1, n_sub_1, z_plus_1);

    printf("Tower height of factorial AST: %zu\n", compute_tower_height(fact_expr));

    env[0] = 5;
    uint64_t res_fact = eval_expr(fact_expr, env, 8);
    printf("5! = %llu\n", (unsigned long long)res_fact);

    free_tree(fact_expr);

    /* Приклад 2. Обмежений пошук найменшого дільника > 1 для числа n */
    /* Pred(z): (n > 1) ∧ (z > 1) ∧ (Rem(n, z) == 0) */
    /* Rem(n, z) == 0  <=> (1 ∸ (n ∸ z * (n / z))) == 1 */
    ExprNode* div_term = make_binop(NODE_MUL, make_var(1), 
                            make_binop(NODE_DIV, make_var(0), make_var(1)));
    ExprNode* rem_term = make_binop(NODE_SUB, make_var(0), div_term);
    ExprNode* rem_is_zero = make_binop(NODE_SUB, make_const(1), rem_term);
    ExprNode* z_gt_1 = make_binop(NODE_SUB, make_var(1), make_const(1)); /* z >= 2 */
    ExprNode* cond_prime_factor = make_binop(NODE_MUL, rem_is_zero, 
                                    make_binop(NODE_SUB, make_const(1), 
                                        make_binop(NODE_SUB, make_const(1), z_gt_1)));

    ExprNode* search_divisor = make_bounded(NODE_SEARCH, 1, make_var(0), cond_prime_factor);

    env[0] = 91; /* 91 = 7 * 13 */
    uint64_t divisor = eval_expr(search_divisor, env, 8);
    printf("Smallest divisor of 91 (> 1): %llu\n", (unsigned long long)divisor);

    free_tree(search_divisor);
    return 0;
}
