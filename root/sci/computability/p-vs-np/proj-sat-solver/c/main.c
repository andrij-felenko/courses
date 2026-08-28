#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

#define MAX_VARS 64
#define MAX_CLAUSES 256
#define MAX_LITS_PER_CLAUSE 8

// Літерал: +x або -x. Кодування: x > 0 означає змінну x, x < 0 означає заперечення x.
typedef struct {
    int lits[MAX_LITS_PER_CLAUSE];
    int size;
} Clause;

typedef struct {
    Clause clauses[MAX_CLAUSES];
    int num_clauses;
    int num_vars;
} Formula;

// Стан змінних: 0 = неоцінено, 1 = True, -1 = False
typedef struct {
    int val[MAX_VARS + 1];
    long long decision_count;
} SolverState;

// Оцінка літерала за поточного стану
static int eval_literal(int lit, const SolverState* st) {
    int var = abs(lit);
    int assign = st->val[var];
    if (assign == 0) return 0;
    return (lit > 0) ? assign : -assign;
}

// Поширення одиничних диз'юнктів (Unit Propagation)
static bool unit_propagation(Formula* f, SolverState* st) {
    bool changed = true;
    while (changed) {
        changed = false;
        for (int i = 0; i < f->num_clauses; i++) {
            Clause* c = &f->clauses[i];
            int unassigned_lit = 0;
            int num_unassigned = 0;
            bool clause_satisfied = false;

            for (int j = 0; j < c->size; j++) {
                int ev = eval_literal(c->lits[j], st);
                if (ev == 1) {
                    clause_satisfied = true;
                    break;
                } else if (ev == 0) {
                    num_unassigned++;
                    unassigned_lit = c->lits[j];
                }
            }

            if (clause_satisfied) continue;

            if (num_unassigned == 0) {
                // Порожній диз'юнкт — суперечність (UNSAT)
                return false;
            }

            if (num_unassigned == 1) {
                // Знайдено одиничний диз'юнкт!
                int var = abs(unassigned_lit);
                st->val[var] = (unassigned_lit > 0) ? 1 : -1;
                changed = true;
            }
        }
    }
    return true;
}

// Усунення чистих літералів (Pure Literal Elimination)
static void pure_literal_elimination(Formula* f, SolverState* st) {
    int pos_count[MAX_VARS + 1] = {0};
    int neg_count[MAX_VARS + 1] = {0};

    for (int i = 0; i < f->num_clauses; i++) {
        Clause* c = &f->clauses[i];
        bool clause_sat = false;
        for (int j = 0; j < c->size; j++) {
            if (eval_literal(c->lits[j], st) == 1) {
                clause_sat = true;
                break;
            }
        }
        if (clause_sat) continue;

        for (int j = 0; j < c->size; j++) {
            if (eval_literal(c->lits[j], st) == 0) {
                int lit = c->lits[j];
                if (lit > 0) pos_count[lit]++;
                else neg_count[-lit]++;
            }
        }
    }

    for (int v = 1; v <= f->num_vars; v++) {
        if (st->val[v] == 0) {
            if (pos_count[v] > 0 && neg_count[v] == 0) {
                st->val[v] = 1;
            } else if (neg_count[v] > 0 && pos_count[v] == 0) {
                st->val[v] = -1;
            }
        }
    }
}

// Перевірка, чи всі диз'юнкти задоволені
static bool is_formula_satisfied(const Formula* f, const SolverState* st) {
    for (int i = 0; i < f->num_clauses; i++) {
        bool clause_sat = false;
        for (int j = 0; j < f->clauses[i].size; j++) {
            if (eval_literal(f->clauses[i].lits[j], st) == 1) {
                clause_sat = true;
                break;
            }
        }
        if (!clause_sat) return false;
    }
    return true;
}

// Пошук першої неоціненої змінної
static int pick_unassigned_variable(const Formula* f, const SolverState* st) {
    for (int v = 1; v <= f->num_vars; v++) {
        if (st->val[v] == 0) return v;
    }
    return 0;
}

// Головна рекурсивна функція DPLL
static bool dpll_recursive(Formula* f, SolverState* st) {
    st->decision_count++;

    // Крок 1: Unit Propagation
    if (!unit_propagation(f, st)) {
        return false; // Виникла суперечність
    }

    // Крок 2: Pure Literal Elimination
    pure_literal_elimination(f, st);

    // Крок 3: Перевірка завершення
    if (is_formula_satisfied(f, st)) {
        return true;
    }

    int var = pick_unassigned_variable(f, st);
    if (var == 0) {
        return is_formula_satisfied(f, st);
    }

    // Збереження стану для можливого повернення (backtrack)
    SolverState backup = *st;

    // Гілка 1: Спробувати var = True
    st->val[var] = 1;
    if (dpll_recursive(f, st)) return true;

    // Гілка 2: Відновлення та спроба var = False
    *st = backup;
    st->val[var] = -1;
    return dpll_recursive(f, st);
}

int main(void) {
    Formula f;
    f.num_vars = 4;
    f.num_clauses = 5;

    // (x1 OR x2) AND (-x1 OR x3) AND (-x2 OR x4) AND (-x3 OR -x4) AND (x1 OR -x4)
    int raw_clauses[5][3] = {
        {1, 2, 0},
        {-1, 3, 0},
        {-2, 4, 0},
        {-3, -4, 0},
        {1, -4, 0}
    };

    for (int i = 0; i < f.num_clauses; i++) {
        f.clauses[i].size = 0;
        for (int j = 0; raw_clauses[i][j] != 0; j++) {
            f.clauses[i].lits[f.clauses[i].size++] = raw_clauses[i][j];
        }
    }

    SolverState st;
    memset(&st, 0, sizeof(st));

    printf("=== Спрощений DPLL SAT-соловер (C) ===\n");
    printf("Вхідні дані: %d змінних, %d диз'юнктів\n", f.num_vars, f.num_clauses);

    bool result = dpll_recursive(&f, &st);

    if (result) {
        printf("Результат: SAT (Формулу можна виконати!)\n");
        printf("Призначення змінних:\n");
        for (int v = 1; v <= f.num_vars; v++) {
            printf("  x%d = %s\n", v, (st.val[v] == 1) ? "True" : (st.val[v] == -1) ? "False" : "Unassigned");
        }
    } else {
        printf("Результат: UNSAT (Формула невиконувана)\n");
    }
    printf("Кількість рішень/рекурсій: %lld\n", st.decision_count);

    return 0;
}
