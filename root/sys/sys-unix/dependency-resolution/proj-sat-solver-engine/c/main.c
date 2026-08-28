#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

#define MAX_VARS 100
#define MAX_CLAUSES 200
#define MAX_LITS_PER_CLAUSE 10

// Структура, що представляє один булевий диз'юнкт (Clause)
typedef struct {
    int lits[MAX_LITS_PER_CLAUSE];
    int size;
} Clause;

// Структура стан SAT-солвера
typedef struct {
    int num_vars;
    int num_clauses;
    Clause clauses[MAX_CLAUSES];
    int assignment[MAX_VARS + 1]; // 0 = unassigned, 1 = true, -1 = false
} SatSolver;

// Ініціалізація структури солвера
void sat_init(SatSolver *solver, int vars) {
    solver->num_vars = vars;
    solver->num_clauses = 0;
    for (int i = 0; i <= vars; i++) {
        solver->assignment[i] = 0;
    }
}

// Додавання диз'юнкта з двох літералів (наприклад, залежність або конфлікт)
void sat_add_clause_2(SatSolver *solver, int lit1, int lit2) {
    if (solver->num_clauses >= MAX_CLAUSES) return;
    Clause *c = &solver->clauses[solver->num_clauses++];
    c->lits[0] = lit1;
    c->lits[1] = lit2;
    c->size = 2;
}

// Додавання одиничного диз'юнкта (запит користувача)
void sat_add_unit_clause(SatSolver *solver, int lit) {
    if (solver->num_clauses >= MAX_CLAUSES) return;
    Clause *c = &solver->clauses[solver->num_clauses++];
    c->lits[0] = lit;
    c->size = 1;
}

// Оцінка стану диз'юнкта: 1 = Satisfied, 0 = Conflict (всі false), -1 = Unresolved
int eval_clause(const SatSolver *solver, const Clause *c, int *unassigned_lit) {
    int unassigned_count = 0;
    int last_unassigned = 0;

    for (int i = 0; i < c->size; i++) {
        int lit = c->lits[i];
        int var = (lit > 0) ? lit : -lit;
        int val = solver->assignment[var];

        // Якщо хоча б один літерал істинний, увесь диз'юнкт є істинним
        if ((lit > 0 && val == 1) || (lit < 0 && val == -1)) {
            return 1;
        }
        // Якщо змінна ще не оцінена
        if (val == 0) {
            unassigned_count++;
            last_unassigned = lit;
        }
    }

    if (unassigned_count == 0) return 0; // Конфлікт! Усі літерали хибні
    if (unassigned_count == 1 && unassigned_lit) *unassigned_lit = last_unassigned;
    return -1; // Диз'юнкт ще не вирішено, є більше одного неоціненого літерала
}

// Реалізація алгоритму Unit Propagation
bool unit_propagate(SatSolver *solver) {
    bool changed = true;
    while (changed) {
        changed = false;
        for (int i = 0; i < solver->num_clauses; i++) {
            int unit_lit = 0;
            int res = eval_clause(solver, &solver->clauses[i], &unit_lit);
            if (res == 0) return false; // Знайдено логічну суперечність
            if (res == -1 && unit_lit != 0) {
                int var = (unit_lit > 0) ? unit_lit : -unit_lit;
                solver->assignment[var] = (unit_lit > 0) ? 1 : -1;
                changed = true;
            }
        }
    }
    return true;
}

// Основна рекурсивна функція пошуку розв'язку (DPLL)
bool solve_dpll(SatSolver *solver) {
    // 1. Виконуємо автоматичне поширення одиничних диз'юнктів
    if (!unit_propagate(solver)) return false;

    // 2. Шукаємо першу неоцінену змінну для прийняття рішення
    int unassigned_var = 0;
    for (int i = 1; i <= solver->num_vars; i++) {
        if (solver->assignment[i] == 0) {
            unassigned_var = i;
            break;
        }
    }

    // Якщо всі змінні оцінені без конфліктів — розв'язок знайдено!
    if (unassigned_var == 0) return true;

    // Зберігаємо поточний стан для можливого відкату
    SatSolver backup = *solver;

    // Гілка А: Спробуємо встановити змінну у True (+1)
    solver->assignment[unassigned_var] = 1;
    if (solve_dpll(solver)) return true;

    // Гілка Б: Відкат та спроба встановити змінну у False (-1)
    *solver = backup;
    solver->assignment[unassigned_var] = -1;
    return solve_dpll(solver);
}

int main(void) {
    SatSolver solver;
    // Створюємо систему з 4 пакунків: 1: App, 2: LibA, 3: Postfix, 4: Sendmail
    sat_init(&solver, 4);

    // Залежність: App вимагає LibA (-1 v 2)
    sat_add_clause_2(&solver, -1, 2);
    // Залежність: App вимагає Postfix (-1 v 3)
    sat_add_clause_2(&solver, -1, 3);
    // Конфлікт: Postfix не сумісний із Sendmail (-3 v -4)
    sat_add_clause_2(&solver, -3, -4);

    // Запит користувача: встановити App (+1)
    sat_add_unit_clause(&solver, 1);

    printf("Аналіз графа залежностей C SAT-солвером...\n");
    if (solve_dpll(&solver)) {
        printf("ЗНАЙДЕНО ЗДІЙСНЕННИЙ ПЛАН ТРАНЗАЦІЇ:\n");
        printf("  - App (ID 1): %s\n", solver.assignment[1] == 1 ? "УСТАНОВИТИ" : "ПРОПУСТИТИ");
        printf("  - LibA (ID 2): %s\n", solver.assignment[2] == 1 ? "УСТАНОВИТИ" : "ПРОПУСТИТИ");
        printf("  - Postfix (ID 3): %s\n", solver.assignment[3] == 1 ? "УСТАНОВИТИ" : "ПРОПУСТИТИ");
        printf("  - Sendmail (ID 4): %s\n", solver.assignment[4] == 1 ? "УСТАНОВИТИ" : "ПРОПУСТИТИ");
    } else {
        printf("ПОМИЛКА: Транзакція неможлива через внутрішній конфлікт залежностей!\n");
    }
    return 0;
}
