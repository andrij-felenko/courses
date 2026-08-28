#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

/* Тип квантора: існування або загальності */
typedef enum {
    QUANT_EXISTS,
    QUANT_FORALL
} QuantifierType;

/* Літерал CNF: змінна var (1-based index) та її полярність (is_pos) */
typedef struct {
    int var;
    bool is_pos;
} Literal;

/* Клауза (диз'юнкція літералів) */
typedef struct {
    Literal* lits;
    size_t count;
} Clause;

/* CNF-формула (кон'юнкція клауз) */
typedef struct {
    Clause* clauses;
    size_t count;
} CNFFormula;

/* Кванторна булева формула в пренексній формі */
typedef struct {
    QuantifierType* quantifiers; /* Масив кванторів розміру num_vars */
    int num_vars;                /* Кількість змінних (1 .. N) */
    CNFFormula cnf;              /* Бескванторне ядро */
} TQBFFormula;

/* Перевірка істинності CNF-формули при заданому призначенні змінних assignment */
static bool evaluate_cnf(const CNFFormula* cnf, const bool* assignment) {
    for (size_t i = 0; i < cnf->count; ++i) {
        const Clause* clause = &cnf->clauses[i];
        bool clause_sat = false;
        
        for (size_t j = 0; j < clause->count; ++j) {
            int var = clause->lits[j].var;
            bool is_pos = clause->lits[j].is_pos;
            bool val = assignment[var];
            
            if ((is_pos && val) || (!is_pos && !val)) {
                clause_sat = true;
                break;
            }
        }
        
        if (!clause_sat) {
            return false; /* Знайдено незадоволену клаузу */
        }
    }
    return true; /* Усі клаузи задоволені */
}

/* Рекурсивна оцінка TQBF у поліномній пам'яті (стек рекурсії = O(num_vars)) */
static bool evaluate_tqbf_recursive(const TQBFFormula* f, int depth, bool* assignment) {
    /* База рекурсії: усі змінні від 1 до num_vars призначені */
    if (depth > f->num_vars) {
        return evaluate_cnf(&f->cnf, assignment);
    }
    
    QuantifierType q = f->quantifiers[depth - 1];
    
    /* Спроба 1: призначення var = false */
    assignment[depth] = false;
    bool res_false = evaluate_tqbf_recursive(f, depth + 1, assignment);
    
    /* Коротке замикання затискає обчислення гілок */
    if (q == QUANT_EXISTS && res_false) {
        return true;
    }
    if (q == QUANT_FORALL && !res_false) {
        return false;
    }
    
    /* Спроба 2: призначення var = true */
    assignment[depth] = true;
    bool res_true = evaluate_tqbf_recursive(f, depth + 1, assignment);
    
    if (q == QUANT_EXISTS) {
        return res_false || res_true;
    } else {
        return res_false && res_true;
    }
}

/* Головний інтерфейс оцінювача TQBF */
bool evaluate_tqbf(const TQBFFormula* f) {
    /* Пам'ять під стек призначень: 1..num_vars (O(N) додаткової пам'яті) */
    bool* assignment = (bool*)calloc((size_t)(f->num_vars + 1), sizeof(bool));
    if (!assignment) return false;
    
    bool result = evaluate_tqbf_recursive(f, 1, assignment);
    free(assignment);
    return result;
}

int main(void) {
    /* Приклад TQBF: ∃x₁ ∀x₂ ((x₁ ∨ x₂) ∧ (x₁ ∨ ¬x₂)) */
    QuantifierType quants[2] = { QUANT_EXISTS, QUANT_FORALL };
    
    Literal c1_lits[2] = { {1, true}, {2, true} };
    Literal c2_lits[2] = { {1, true}, {2, false} };
    
    Clause clauses[2] = {
        { c1_lits, 2 },
        { c2_lits, 2 }
    };
    
    TQBFFormula formula = {
        .quantifiers = quants,
        .num_vars = 2,
        .cnf = { clauses, 2 }
    };
    
    bool is_true = evaluate_tqbf(&formula);
    printf("Формула ∃x₁ ∀x₂ ((x₁ ∨ x₂) ∧ (x₁ ∨ ¬x₂)) є: %s\n",
           is_true ? "ІСТИННОЮ (True)" : "ХИБНОЮ (False)");
           
    return 0;
}
