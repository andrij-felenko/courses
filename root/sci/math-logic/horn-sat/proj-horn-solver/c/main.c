#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>

#define VAR_NONE -1

typedef enum {
    HORN_SAT = 0,
    HORN_UNSAT = 1,
    HORN_ERR_MEM = 2
} HornStatus;

typedef struct AdjNode {
    int clause_id;
    struct AdjNode* next;
} AdjNode;

typedef struct {
    int num_vars;
    int num_clauses;
    int clause_capacity;
    
    int* head;            /* head[c]: голова диз'юнкта або VAR_NONE */
    int* count;           /* count[c]: к-сть неодинечних умов у тілі */
    
    AdjNode** body_adj;   /* body_adj[x]: список диз'юнктів, де x є в умові */
    int* assignment;      /* assignment[x]: 1 або 0 */
    
    int* queue;           /* Черга змінних для поширення */
    int q_head;
    int q_tail;
} HornSolverC;

HornSolverC* horn_solver_create(int num_vars) {
    HornSolverC* solver = (HornSolverC*)malloc(sizeof(HornSolverC));
    if (!solver) return NULL;

    solver->num_vars = num_vars;
    solver->num_clauses = 0;
    solver->clause_capacity = 16;

    solver->head = (int*)malloc(solver->clause_capacity * sizeof(int));
    solver->count = (int*)malloc(solver->clause_capacity * sizeof(int));
    solver->body_adj = (AdjNode**)calloc(num_vars, sizeof(AdjNode*));
    solver->assignment = (int*)calloc(num_vars, sizeof(int));
    solver->queue = (int*)malloc(num_vars * sizeof(int));
    solver->q_head = 0;
    solver->q_tail = 0;

    if (!solver->head || !solver->count || !solver->body_adj || 
        !solver->assignment || !solver->queue) {
        free(solver->head); free(solver->count); free(solver->body_adj);
        free(solver->assignment); free(solver->queue); free(solver);
        return NULL;
    }
    return solver;
}

static bool ensure_clause_capacity(HornSolverC* solver) {
    if (solver->num_clauses >= solver->clause_capacity) {
        int new_cap = solver->clause_capacity * 2;
        int* new_head = (int*)realloc(solver->head, new_cap * sizeof(int));
        int* new_count = (int*)realloc(solver->count, new_cap * sizeof(int));
        if (!new_head || !new_count) return false;
        solver->head = new_head;
        solver->count = new_count;
        solver->clause_capacity = new_cap;
    }
    return true;
}

bool horn_solver_add_clause(HornSolverC* solver, const int* body, int body_size, int head_var) {
    if (!ensure_clause_capacity(solver)) return false;

    int c_id = solver->num_clauses++;
    solver->head[c_id] = head_var;
    solver->count[c_id] = body_size;

    for (int i = 0; i < body_size; ++i) {
        int var = body[i];
        AdjNode* node = (AdjNode*)malloc(sizeof(AdjNode));
        if (!node) return false;
        node->clause_id = c_id;
        node->next = solver->body_adj[var];
        solver->body_adj[var] = node;
    }

    /* Якщо це факт (порожнє тіло та наявна голова) */
    if (body_size == 0 && head_var != VAR_NONE) {
        if (solver->assignment[head_var] == 0) {
            solver->assignment[head_var] = 1;
            solver->queue[solver->q_tail++] = head_var;
        }
    }
    return true;
}

HornStatus horn_solver_solve(HornSolverC* solver) {
    while (solver->q_head < solver->q_tail) {
        int u = solver->queue[solver->q_head++];
        AdjNode* curr = solver->body_adj[u];

        while (curr) {
            int c_id = curr->clause_id;
            solver->count[c_id]--;

            if (solver->count[c_id] == 0) {
                int h = solver->head[c_id];
                if (h == VAR_NONE) {
                    return HORN_UNSAT; /* Виявлено суперечність із обмеженням */
                }
                if (solver->assignment[h] == 0) {
                    solver->assignment[h] = 1;
                    solver->queue[solver->q_tail++] = h;
                }
            }
            curr = curr->next;
        }
    }
    return HORN_SAT;
}

void horn_solver_free(HornSolverC* solver) {
    if (!solver) return;
    for (int i = 0; i < solver->num_vars; ++i) {
        AdjNode* curr = solver->body_adj[i];
        while (curr) {
            AdjNode* tmp = curr;
            curr = curr->next;
            free(tmp);
        }
    }
    free(solver->head);
    free(solver->count);
    free(solver->body_adj);
    free(solver->assignment);
    free(solver->queue);
    free(solver);
}

int main(void) {
    /* Приклад: A=0, B=1, C=2, D=3 */
    HornSolverC* solver = horn_solver_create(4);

    /* Факти: A = 1, D = 1 */
    horn_solver_add_clause(solver, NULL, 0, 0); /* ⊤ → A */
    horn_solver_add_clause(solver, NULL, 0, 3); /* ⊤ → D */

    /* Правила: (A) → B, (B ∧ D) → C */
    int r1_body[] = {0};
    horn_solver_add_clause(solver, r1_body, 1, 1);

    int r2_body[] = {1, 3};
    horn_solver_add_clause(solver, r2_body, 2, 2);

    /* Обмеження: (C ∧ A) → ⊥ */
    int c1_body[] = {2, 0};
    horn_solver_add_clause(solver, c1_body, 2, VAR_NONE);

    HornStatus res = horn_solver_solve(solver);
    if (res == HORN_SAT) {
        printf("Результат: SAT. Мінімальна модель:\n");
        for (int i = 0; i < 4; ++i) {
            printf("  Змінна %d = %d\n", i, solver->assignment[i]);
        }
    } else {
        printf("Результат: UNSAT (виявлено суперечність).\n");
    }

    horn_solver_free(solver);
    return 0;
}
