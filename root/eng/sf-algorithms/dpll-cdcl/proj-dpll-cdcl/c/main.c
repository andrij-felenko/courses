#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

#define L_UNDEFINED -1
#define L_FALSE      0
#define L_TRUE       1

typedef struct {
    int* lits;
    int size;
    int lbd;
} Clause;

typedef struct {
    int var;
    int val;
    int level;
    Clause* reason;
} TrailEntry;

typedef struct {
    int num_vars;
    int num_clauses;
    Clause** clauses;
    int* assigns;       /* assigns[var] -> L_UNDEFINED, L_FALSE, L_TRUE */
    int* levels;        /* levels[var] -> decision level */
    Clause** reasons;   /* reasons[var] -> clause that forced assignment */
    double* activity;   /* VSIDS activity scores */
    TrailEntry* trail;
    int trail_size;
    int trail_capacity;
    int current_level;
    double var_inc;
    double var_decay;
} CDCLSolver;

CDCLSolver* solver_create(int num_vars) {
    CDCLSolver* s = (CDCLSolver*)malloc(sizeof(CDCLSolver));
    s->num_vars = num_vars;
    s->num_clauses = 0;
    s->clauses = NULL;
    s->assigns = (int*)malloc((num_vars + 1) * sizeof(int));
    s->levels = (int*)malloc((num_vars + 1) * sizeof(int));
    s->reasons = (Clause**)malloc((num_vars + 1) * sizeof(Clause*));
    s->activity = (double*)malloc((num_vars + 1) * sizeof(double));
    
    for (int i = 1; i <= num_vars; i++) {
        s->assigns[i] = L_UNDEFINED;
        s->levels[i] = -1;
        s->reasons[i] = NULL;
        s->activity[i] = 0.0;
    }
    
    s->trail_capacity = 1024;
    s->trail_size = 0;
    s->trail = (TrailEntry*)malloc(s->trail_capacity * sizeof(TrailEntry));
    s->current_level = 0;
    s->var_inc = 1.0;
    s->var_decay = 0.95;
    return s;
}

void solver_free(CDCLSolver* s) {
    if (!s) return;
    for (int i = 0; i < s->num_clauses; i++) {
        free(s->clauses[i]->lits);
        free(s->clauses[i]);
    }
    free(s->clauses);
    free(s->assigns);
    free(s->levels);
    free(s->reasons);
    free(s->activity);
    free(s->trail);
    free(s);
}

void solver_add_clause(CDCLSolver* s, const int* lits, int size) {
    Clause* c = (Clause*)malloc(sizeof(Clause));
    c->size = size;
    c->lbd = 0;
    c->lits = (int*)malloc(size * sizeof(int));
    for (int i = 0; i < size; i++) {
        c->lits[i] = lits[i];
    }
    
    s->num_clauses++;
    s->clauses = (Clause**)realloc(s->clauses, s->num_clauses * sizeof(Clause*));
    s->clauses[s->num_clauses - 1] = c;
}

static inline int lit_value(CDCLSolver* s, int lit) {
    int var = abs(lit);
    int val = s->assigns[var];
    if (val == L_UNDEFINED) return L_UNDEFINED;
    return (lit > 0) ? val : (1 - val);
}

void solver_assign(CDCLSolver* s, int lit, Clause* reason) {
    int var = abs(lit);
    int val = (lit > 0) ? L_TRUE : L_FALSE;
    s->assigns[var] = val;
    s->levels[var] = s->current_level;
    s->reasons[var] = reason;
    
    if (s->trail_size >= s->trail_capacity) {
        s->trail_capacity *= 2;
        s->trail = (TrailEntry*)realloc(s->trail, s->trail_capacity * sizeof(TrailEntry));
    }
    s->trail[s->trail_size].var = var;
    s->trail[s->trail_size].val = val;
    s->trail[s->trail_size].level = s->current_level;
    s->trail[s->trail_size].reason = reason;
    s->trail_size++;
}

Clause* solver_bcp(CDCLSolver* s) {
    for (int i = 0; i < s->num_clauses; i++) {
        Clause* c = s->clauses[i];
        int false_count = 0;
        int undef_lit = 0;
        int undef_count = 0;
        
        for (int j = 0; j < c->size; j++) {
            int val = lit_value(s, c->lits[j]);
            if (val == L_TRUE) {
                undef_count = -1; /* Clause already satisfied */
                break;
            }
            if (val == L_FALSE) {
                false_count++;
            } else {
                undef_count++;
                undef_lit = c->lits[j];
            }
        }
        
        if (undef_count == -1) continue;
        
        if (false_count == c->size) {
            return c; /* Conflict detected! */
        }
        
        if (undef_count == 1) {
            solver_assign(s, undef_lit, c);
        }
    }
    return NULL;
}

void solver_backtrack(CDCLSolver* s, int target_level) {
    while (s->trail_size > 0 && s->trail[s->trail_size - 1].level > target_level) {
        TrailEntry entry = s->trail[--s->trail_size];
        s->assigns[entry.var] = L_UNDEFINED;
        s->levels[entry.var] = -1;
        s->reasons[entry.var] = NULL;
    }
    s->current_level = target_level;
}

void solver_bump_var(CDCLSolver* s, int var) {
    s->activity[var] += s->var_inc;
    if (s->activity[var] > 1e100) {
        for (int i = 1; i <= s->num_vars; i++) {
            s->activity[i] *= 1e-100;
        }
        s->var_inc *= 1e-100;
    }
}

int solver_pick_variable(CDCLSolver* s) {
    int best_var = 0;
    double max_act = -1.0;
    for (int i = 1; i <= s->num_vars; i++) {
        if (s->assigns[i] == L_UNDEFINED) {
            if (s->activity[i] > max_act) {
                max_act = s->activity[i];
                best_var = i;
            }
        }
    }
    return best_var;
}

bool solver_solve(CDCLSolver* s) {
    while (true) {
        Clause* conflict = solver_bcp(s);
        if (conflict != NULL) {
            if (s->current_level == 0) return false; /* UNSAT */
            
            /* Non-chronological Backtrack to previous decision level */
            solver_backtrack(s, s->current_level - 1);
            continue;
        }
        
        int next_var = solver_pick_variable(s);
        if (next_var == 0) return true; /* SAT: all variables assigned */
        
        s->current_level++;
        solver_assign(s, next_var, NULL);
    }
}

int main(void) {
    CDCLSolver* s = solver_create(3);
    
    /* F = (x₁ ∨ x₂) ∧ (¬x₁ ∨ x₃) ∧ (¬x₂ ∨ ¬x₃) */
    int c1[] = {1, 2};
    int c2[] = {-1, 3};
    int c3[] = {-2, -3};
    
    solver_add_clause(s, c1, 2);
    solver_add_clause(s, c2, 2);
    solver_add_clause(s, c3, 2);
    
    if (solver_solve(s)) {
        printf("SAT! Assigns: x1=%d, x2=%d, x3=%d\n", s->assigns[1], s->assigns[2], s->assigns[3]);
    } else {
        printf("UNSAT!\n");
    }
    
    solver_free(s);
    return 0;
}
