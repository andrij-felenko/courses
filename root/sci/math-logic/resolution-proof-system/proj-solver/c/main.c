#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>

#define MAX_LITS_PER_CLAUSE 64
#define MAX_CLAUSES 1024

// Структура диз'юнкта
typedef struct {
    int lits[MAX_LITS_PER_CLAUSE];
    size_t size;
} Clause;

// Структура формули КНФ
typedef struct {
    Clause clauses[MAX_CLAUSES];
    size_t count;
} CNFFormula;

// Допоміжна функція порівняння для qsort
static int compare_literals(const void *a, const void *b) {
    int l1 = *(const int *)a;
    int l2 = *(const int *)b;
    if (abs(l1) != abs(l2)) return abs(l1) - abs(l2);
    return l1 - l2;
}

// Нормалізація диз'юнкта: сортування та вилучення дублікатів
// Повертає false, якщо диз'юнкт є тавтологією (містить x і -x)
bool normalize_clause(Clause *c) {
    if (c->size <= 1) return true;
    
    qsort(c->lits, c->size, sizeof(int), compare_literals);
    
    size_t new_size = 0;
    for (size_t i = 0; i < c->size; i++) {
        if (i > 0 && c->lits[i] == c->lits[i - 1]) {
            continue; // Дублікат літерала
        }
        if (i > 0 && c->lits[i] == -c->lits[i - 1]) {
            return false; // Тавтологія: містить y та -y
        }
        c->lits[new_size++] = c->lits[i];
    }
    c->size = new_size;
    return true;
}

// Перевірка, чи диз'юнкт є порожнім ⊥
bool is_empty_clause(const Clause *c) {
    return c->size == 0;
}

// Перевірка рівності двох диз'юнктів
bool clauses_equal(const Clause *c1, const Clause *c2) {
    if (c1->size != c2->size) return false;
    for (size_t i = 0; i < c1->size; i++) {
        if (c1->lits[i] != c2->lits[i]) return false;
    }
    return true;
}

// Виконання резолюції між c1 та c2 за змінною pivot_var (pivot_var > 0)
// Повертає true, якщо резольвента створена успішно і не є тавтологією
bool resolve_clauses(const Clause *c1, const Clause *c2, int pivot_var, Clause *out_res) {
    bool found_pos = false, found_neg = false;
    
    // Перевіряємо полярність pivot у c1 та c2
    for (size_t i = 0; i < c1->size; i++) {
        if (c1->lits[i] == pivot_var) found_pos = true;
        if (c1->lits[i] == -pivot_var) found_neg = true;
    }
    bool c2_pos = false, c2_neg = false;
    for (size_t i = 0; i < c2->size; i++) {
        if (c2->lits[i] == pivot_var) c2_pos = true;
        if (c2->lits[i] == -pivot_var) c2_neg = true;
    }
    
    if (!((found_pos && c2_neg) || (found_neg && c2_pos))) {
        return false; // Немає комплементарної пари за pivot_var
    }
    
    out_res->size = 0;
    
    // Копіюємо літерали з c1, крім pivot
    for (size_t i = 0; i < c1->size; i++) {
        if (abs(c1->lits[i]) != pivot_var) {
            out_res->lits[out_res->size++] = c1->lits[i];
        }
    }
    // Копіюємо літерали з c2, крім pivot
    for (size_t i = 0; i < c2->size; i++) {
        if (abs(c2->lits[i]) != pivot_var) {
            if (out_res->size >= MAX_LITS_PER_CLAUSE) return false;
            out_res->lits[out_res->size++] = c2->lits[i];
        }
    }
    
    return normalize_clause(out_res);
}

// Перевірка, чи міститься диз'юнкт у формулі
bool formula_contains(const CNFFormula *formula, const Clause *c) {
    for (size_t i = 0; i < formula->count; i++) {
        if (clauses_equal(&formula->clauses[i], c)) return true;
    }
    return false;
}

// Головний алгоритм резолюційного спростування (насичення)
// Повертає true, якщо формула НЕЗДІЙСНЕННА (виведено ⊥)
bool resolution_refute(CNFFormula *formula, int max_variables) {
    printf("[Спростування] Початкова кількість диз'юнктів: %zu\n", formula->count);
    
    // Нормалізуємо початкові диз'юнкти
    size_t valid_cnt = 0;
    for (size_t i = 0; i < formula->count; i++) {
        if (normalize_clause(&formula->clauses[i])) {
            if (is_empty_clause(&formula->clauses[i])) {
                printf("[Резолюція] Знайдено порожній диз'юнкт у початковій КНФ!\n");
                return true;
            }
            formula->clauses[valid_cnt++] = formula->clauses[i];
        }
    }
    formula->count = valid_cnt;

    size_t added_in_pass = 1;
    size_t pass = 1;

    while (added_in_pass > 0) {
        added_in_pass = 0;
        size_t current_count = formula->count;
        printf("--- Ітерація насичення %zu (диз'юнктів: %zu) ---\n", pass++, current_count);

        for (size_t i = 0; i < current_count; i++) {
            for (size_t j = i + 1; j < current_count; j++) {
                for (int v = 1; v <= max_variables; v++) {
                    Clause res;
                    if (resolve_clauses(&formula->clauses[i], &formula->clauses[j], v, &res)) {
                        if (is_empty_clause(&res)) {
                            printf("[УСПІХ] Виведено порожній диз'юнкт ⊥ на кроці %zu!\n", pass);
                            return true; // UNSAT
                        }
                        if (!formula_contains(formula, &res)) {
                            if (formula->count < MAX_CLAUSES) {
                                formula->clauses[formula->count++] = res;
                                added_in_pass++;
                            }
                        }
                    }
                }
            }
        }
    }
    
    printf("[РЕЗУЛЬТАТ] Можливе насичення без виводу ⊥. Формула здійсненна (SAT).\n");
    return false;
}

int main(void) {
    // Тестова КНФ нездійсненна: (x1 ∨ x2) ∧ (¬x1 ∨ x2) ∧ (x1 ∨ ¬x2) ∧ (¬x1 ∨ ¬x2)
    CNFFormula formula = {
        .clauses = {
            {.lits = {1, 2}, .size = 2},
            {.lits = {-1, 2}, .size = 2},
            {.lits = {1, -2}, .size = 2},
            {.lits = {-1, -2}, .size = 2}
        },
        .count = 4
    };

    bool is_unsat = resolution_refute(&formula, 2);
    printf("Формула нездійсненна (UNSAT): %s\n", is_unsat ? "ТАК" : "НІ");
    return 0;
}
