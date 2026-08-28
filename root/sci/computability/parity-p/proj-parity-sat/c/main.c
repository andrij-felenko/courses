#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

#define MAX_VARS 32
#define MAX_CLAUSES 64

typedef struct {
    int vars[MAX_VARS];
    int len;
} Clause;

typedef struct {
    Clause clauses[MAX_CLAUSES];
    int num_clauses;
    int num_vars;
} Formula;

/* Створення нової порожньої формули */
Formula* formula_create(int num_vars) {
    Formula* f = (Formula*)malloc(sizeof(Formula));
    if (!f) return NULL;
    f->num_vars = num_vars;
    f->num_clauses = 0;
    return f;
}

/* Додавання диз'юнкта до формули */
void formula_add_clause(Formula* f, const int* literals, int len) {
    if (f->num_clauses >= MAX_CLAUSES) return;
    Clause* c = &f->clauses[f->num_clauses++];
    c->len = len;
    for (int i = 0; i < len; i++) {
        c->vars[i] = literals[i];
    }
}

/* Звільнення пам'яті */
void formula_free(Formula* f) {
    free(f);
}

/* Рекурсивний обчислювач парності ⊕SAT (mod 2) */
int solve_parity_sat_rec(Formula* f, int var_idx, int* assignment) {
    if (var_idx > f->num_vars) {
        /* Перевірка, чи всі диз'юнкти істинні при даному присвоєнні */
        for (int i = 0; i < f->num_clauses; i++) {
            bool clause_sat = false;
            for (int j = 0; j < f->clauses[i].len; j++) {
                int lit = f->clauses[i].vars[j];
                int var = (lit > 0) ? lit : -lit;
                bool val = (assignment[var] == 1);
                if (lit < 0) val = !val;
                if (val) {
                    clause_sat = true;
                    break;
                }
            }
            if (!clause_sat) return 0; /* Нездійсненна гілка */
        }
        return 1; /* Здійсненний свідок (+1 mod 2) */
    }

    /* Розгалуження за змінною var_idx: присвоєння 0 та 1 */
    assignment[var_idx] = 0;
    int left_parity = solve_parity_sat_rec(f, var_idx + 1, assignment);

    assignment[var_idx] = 1;
    int right_parity = solve_parity_sat_rec(f, var_idx + 1, assignment);

    /* Додавання за модулем 2 (операція XOR) */
    return (left_parity ^ right_parity);
}

/* Головна функція обчислення парності ⊕SAT */
int compute_parity_sat(Formula* f) {
    int assignment[MAX_VARS + 1];
    memset(assignment, 0, sizeof(assignment));
    return solve_parity_sat_rec(f, 1, assignment);
}

int main(void) {
    /* Формула: (x1 OR x2) AND (NOT x1 OR x3) AND (x2 OR NOT x3) */
    Formula* f = formula_create(3);
    
    int c1[] = {1, 2};
    int c2[] = {-1, 3};
    int c3[] = {2, -3};

    formula_add_clause(f, c1, 2);
    formula_add_clause(f, c2, 2);
    formula_add_clause(f, c3, 2);

    int parity = compute_parity_sat(f);
    printf("Кількість розв'язків непарна? %s (Parity = %d)\n",
           parity ? "ТАК" : "НІ", parity);

    formula_free(f);
    return 0;
}
