#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>

/* Структура для представлення диз'юнкта (clause):
 * Літерали кодуються цілими числами:
 * +1 означає x1, -1 означає NOT x1. 
 */
typedef struct {
    int* lits;
    size_t lit_count;
} Clause;

typedef struct {
    size_t var_count;
    size_t clause_count;
    Clause* clauses;
} CNFFormula;

/* Оцінка диз'юнкта при частковому або повному призначенні:
 * Повертає 1 (TRUE), 0 (FALSE), або -1 (НЕВИЗНАЧЕНО).
 */
static int eval_clause(const Clause* c, const int8_t* assignment) {
    bool has_undef = false;
    for (size_t i = 0; i < c->lit_count; ++i) {
        int lit = c->lits[i];
        size_t var_idx = (size_t)(abs(lit) - 1);
        int8_t val = assignment[var_idx];
        
        if (val == -1) {
            has_undef = true;
        } else if ((lit > 0 && val == 1) || (lit < 0 && val == 0)) {
            return 1; /* Диз'юнкт істинний */
        }
    }
    return has_undef ? -1 : 0;
}

/* Оцінка всієї КНФ-формули */
static int eval_formula(const CNFFormula* f, const int8_t* assignment) {
    bool has_undef = false;
    for (size_t i = 0; i < f->clause_count; ++i) {
        int res = eval_clause(&f->clauses[i], assignment);
        if (res == 0) return 0; /* Один хибний диз'юнкт робить усю формулу хибною */
        if (res == -1) has_undef = true;
    }
    return has_undef ? -1 : 1;
}

/* Рекурсивний підрахунок кількості виконуючих наборів */
static uint64_t count_sat_rec(const CNFFormula* f, size_t var_idx, int8_t* assignment, uint64_t threshold) {
    int status = eval_formula(f, assignment);
    
    if (status == 0) {
        return 0; /* Раннє відтинання: формула вже хибна */
    }
    
    if (var_idx == f->var_count) {
        return (status == 1) ? 1ULL : 0ULL;
    }
    
    /* Якщо всі диз'юнкти вже істинні, всі залишок 2^(N - var_idx) гілок будуть істинними */
    if (status == 1) {
        return 1ULL << (f->var_count - var_idx);
    }

    /* Гілка 1: присвоюємо var_idx = 0 */
    assignment[var_idx] = 0;
    uint64_t count_left = count_sat_rec(f, var_idx + 1, assignment, threshold);

    /* Гілка 2: присвоюємо var_idx = 1 */
    assignment[var_idx] = 1;
    uint64_t count_right = count_sat_rec(f, var_idx + 1, assignment, threshold);

    /* Відновлюємо стан для зворотного ходу */
    assignment[var_idx] = -1;

    return count_left + count_right;
}

/* Головна функція перевірки належності до MAJSAT */
bool solve_majsat(const CNFFormula* f, uint64_t* out_sat_count) {
    int8_t* assignment = (int8_t*)malloc(f->var_count * sizeof(int8_t));
    for (size_t i = 0; i < f->var_count; ++i) {
        assignment[i] = -1; /* -1 означає невизначену змінну */
    }

    uint64_t total_paths = 1ULL << f->var_count;
    uint64_t threshold = total_paths / 2;

    uint64_t sat_count = count_sat_rec(f, 0, assignment, threshold);
    free(assignment);

    if (out_sat_count) {
        *out_sat_count = sat_count;
    }

    return sat_count > threshold;
}

int main(void) {
    /* Приклад КНФ з 3 змінними: (x1 OR x2) AND (NOT x1 OR x3) */
    size_t num_vars = 3;
    size_t num_clauses = 2;

    Clause clauses[2];
    int c1_lits[] = {1, 2};   /* x1 OR x2 */
    int c2_lits[] = {-1, 3};  /* NOT x1 OR x3 */

    clauses[0].lits = c1_lits; clauses[0].lit_count = 2;
    clauses[1].lits = c2_lits; clauses[1].lit_count = 2;

    CNFFormula formula = {num_vars, num_clauses, clauses};

    uint64_t sat_count = 0;
    bool is_majsat = solve_majsat(&formula, &sat_count);

    printf("Кількість змінних: %zu (всього гілок: %llu)\n", num_vars, 1ULL << num_vars);
    printf("Кількість виконуючих наборів N_sat: %llu\n", (unsigned long long)sat_count);
    printf("Поріг більшості (> %llu): %s\n", (unsigned long long)((1ULL << num_vars) / 2),
           is_majsat ? "ТАК (належить до MAJSAT)" : "НІ (не належить до MAJSAT)");

    return 0;
}
