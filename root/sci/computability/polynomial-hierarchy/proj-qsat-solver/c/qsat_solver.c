/* qsat_solver.c — Ідіоматичний розв'язувач 2-QSAT мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

typedef enum {
    QUANT_EXISTS,
    QUANT_FORALL
} QuantifierType;

typedef struct {
    int variable_id;
    QuantifierType type;
} VariableQuant;

typedef struct {
    int* literals; /* Позитивні значення: variable_id; Негативні: -variable_id */
    size_t size;
} Clause;

typedef struct {
    size_t num_vars;
    size_t num_clauses;
    VariableQuant* quantifiers; /* Масив кванторів у порядку їхнього чергування */
    Clause* clauses;
} QBFFormula;

/* Оцінка одного диз'юнкта при заданому призначенні змінних:
   values[i] = 1 (істина), 0 (хиба), -1 (непризначено) */
static int eval_clause(const Clause* clause, const int* values) {
    bool has_unassigned = false;
    for (size_t i = 0; i < clause->size; ++i) {
        int lit = clause->literals[i];
        int var = abs(lit);
        int val = values[var];
        
        if (val == -1) {
            has_unassigned = true;
        } else {
            bool is_positive = (lit > 0);
            if ((is_positive && val == 1) || (!is_positive && val == 0)) {
                return 1; /* Диз'юнкт істинний */
            }
        }
    }
    return has_unassigned ? -1 : 0; /* -1: ще не визначено, 0: точно хибний */
}

/* Оцінка всієї КНФ формули */
static int eval_formula(const QBFFormula* formula, const int* values) {
    bool has_undef = false;
    for (size_t i = 0; i < formula->num_clauses; ++i) {
        int res = eval_clause(&formula->clauses[i], values);
        if (res == 0) return 0; /* Якщо хоч один диз'юнкт 0, вся КНФ = 0 */
        if (res == -1) has_undef = true;
    }
    return has_undef ? -1 : 1;
}

/* Рекурсивний розв'язувач QSAT з чергуванням кванторів */
static bool solve_qsat_rec(const QBFFormula* formula, size_t var_idx, int* values) {
    int status = eval_formula(formula, values);
    if (status == 1) return true;
    if (status == 0) return false;
    if (var_idx > formula->num_vars) return false;

    int var_id = formula->quantifiers[var_idx - 1].variable_id;
    QuantifierType qtype = formula->quantifiers[var_idx - 1].type;

    if (qtype == QUANT_EXISTS) {
        /* Квантор ∃: Достатньо, щоб хоча б одне значення дало true (АБО) */
        values[var_id] = 0;
        if (solve_qsat_rec(formula, var_idx + 1, values)) {
            values[var_id] = -1;
            return true;
        }
        values[var_id] = 1;
        bool res = solve_qsat_rec(formula, var_idx + 1, values);
        values[var_id] = -1;
        return res;
    } else {
        /* Квантор ∀: Вимагається, щоб ОБИДВА значення дали true (І) */
        values[var_id] = 0;
        if (!solve_qsat_rec(formula, var_idx + 1, values)) {
            values[var_id] = -1;
            return false; /* Раннє відсікання: 0 на першій гілці нищить ∀ */
        }
        values[var_id] = 1;
        bool res = solve_qsat_rec(formula, var_idx + 1, values);
        values[var_id] = -1;
        return res;
    }
}

bool solve_qbf(const QBFFormula* formula) {
    int* values = (int*)malloc((formula->num_vars + 1) * sizeof(int));
    for (size_t i = 0; i <= formula->num_vars; ++i) values[i] = -1;
    
    bool result = solve_qsat_rec(formula, 1, values);
    free(values);
    return result;
}

int main(void) {
    /* Приклад формули: ∃ x1 ∀ y2 [ (x1 OR y2) AND (x1 OR NOT y2) ] */
    QBFFormula f;
    f.num_vars = 2;
    f.num_clauses = 2;

    VariableQuant quants[2] = {
        {1, QUANT_EXISTS},
        {2, QUANT_FORALL}
    };
    f.quantifiers = quants;

    Clause clauses[2];
    int l1[2] = {1, 2};   /* x1 OR y2 */
    int l2[2] = {1, -2};  /* x1 OR NOT y2 */
    clauses[0].literals = l1; clauses[0].size = 2;
    clauses[1].literals = l2; clauses[1].size = 2;
    f.clauses = clauses;

    bool ans = solve_qbf(&f);
    printf("Результат оцінки ∃x1 ∀y2 [(x1 OR y2) AND (x1 OR !y2)]: %s\n", 
           ans ? "TRUE (ІСТИНА)" : "FALSE (ХИБА)");

    return 0;
}
