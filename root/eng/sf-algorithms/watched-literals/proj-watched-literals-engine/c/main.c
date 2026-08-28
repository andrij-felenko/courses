/* c */
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

typedef int Literal;
typedef int Var;

#define LIT_VAR(lit) ((lit) >> 1)
#define LIT_SIGN(lit) ((lit) & 1)
#define LIT_MAKE(v, sign) (((v) << 1) | ((sign) ? 1 : 0))
#define LIT_NEG(lit) ((lit) ^ 1)

typedef enum {
    VAL_FALSE = -1,
    VAL_UNASSIGNED = 0,
    VAL_TRUE = 1
} VarValue;

typedef struct {
    int size;
    Literal* lits;
} Clause;

typedef struct {
    int clause_id;
    Literal blocker;
} Watcher;

typedef struct {
    Watcher* data;
    int capacity;
    int size;
} WatchList;

typedef struct {
    int num_vars;
    VarValue* values;
    int* assign_levels;
    
    Clause** clauses;
    int num_clauses;
    
    WatchList* watches; // Масив розміром 2 * (num_vars + 1)
    
    Literal* trail;
    int trail_size;
    int trail_head;
    
    int current_level;
} Solver;

Solver* solver_create(int num_vars) {
    Solver* s = (Solver*)malloc(sizeof(Solver));
    s->num_vars = num_vars;
    s->values = (VarValue*)calloc(num_vars + 1, sizeof(VarValue));
    s->assign_levels = (int*)calloc(num_vars + 1, sizeof(int));
    
    s->clauses = NULL;
    s->num_clauses = 0;
    
    int num_lits = 2 * (num_vars + 1);
    s->watches = (WatchList*)calloc(num_lits, sizeof(WatchList));
    
    s->trail = (Literal*)malloc(sizeof(Literal) * (num_vars + 1));
    s->trail_size = 0;
    s->trail_head = 0;
    s->current_level = 0;
    
    return s;
}

void solver_free(Solver* s) {
    for (int i = 0; i < s->num_clauses; i++) {
        free(s->clauses[i]->lits);
        free(s->clauses[i]);
    }
    free(s->clauses);
    
    int num_lits = 2 * (s->num_vars + 1);
    for (int i = 0; i < num_lits; i++) {
        free(s->watches[i].data);
    }
    free(s->watches);
    
    free(s->values);
    free(s->assign_levels);
    free(s->trail);
    free(s);
}

static void watch_list_add(WatchList* wl, int clause_id, Literal blocker) {
    if (wl->size >= wl->capacity) {
        wl->capacity = (wl->capacity == 0) ? 4 : wl->capacity * 2;
        wl->data = (Watcher*)realloc(wl->data, sizeof(Watcher) * wl->capacity);
    }
    wl->data[wl->size].clause_id = clause_id;
    wl->data[wl->size].blocker = blocker;
    wl->size++;
}

VarValue solver_lit_value(Solver* s, Literal lit) {
    Var v = LIT_VAR(lit);
    VarValue val = s->values[v];
    if (val == VAL_UNASSIGNED) return VAL_UNASSIGNED;
    return LIT_SIGN(lit) ? -val : val;
}

void solver_enqueue(Solver* s, Literal lit) {
    Var v = LIT_VAR(lit);
    s->values[v] = LIT_SIGN(lit) ? VAL_FALSE : VAL_TRUE;
    s->assign_levels[v] = s->current_level;
    s->trail[s->trail_size++] = lit;
}

void add_clause(Solver* s, Literal* lits, int size) {
    Clause* c = (Clause*)malloc(sizeof(Clause));
    c->size = size;
    c->lits = (Literal*)malloc(sizeof(Literal) * size);
    for (int i = 0; i < size; i++) {
        c->lits[i] = lits[i];
    }
    
    int cid = s->num_clauses++;
    s->clauses = (Clause**)realloc(s->clauses, sizeof(Clause*) * s->num_clauses);
    s->clauses[cid] = c;
    
    if (size >= 2) {
        watch_list_add(&s->watches[lits[0]], cid, lits[1]);
        watch_list_add(&s->watches[lits[1]], cid, lits[0]);
    }
}

bool solver_propagate(Solver* s, int* conflict_clause_out) {
    while (s->trail_head < s->trail_size) {
        Literal p = s->trail[s->trail_head++];
        Literal false_lit = LIT_NEG(p);
        WatchList* wl = &s->watches[false_lit];
        
        int i = 0, j = 0;
        while (i < wl->size) {
            Watcher w = wl->data[i];
            Clause* c = s->clauses[w.clause_id];
            
            // Перевірка блокуючого літерала
            if (solver_lit_value(s, w.blocker) == VAL_TRUE) {
                wl->data[j++] = w;
                i++;
                continue;
            }
            
            // Перестановка: пересвідчимося, що false_lit є у lits[0]
            if (c->lits[1] == false_lit) {
                c->lits[1] = c->lits[0];
                c->lits[0] = false_lit;
            }
            
            Literal first = c->lits[0];
            Literal second = c->lits[1];
            
            if (solver_lit_value(s, second) == VAL_TRUE) {
                wl->data[j++] = (Watcher){ w.clause_id, second };
                i++;
                continue;
            }
            
            // Сканування нових кандидатів для заміни w[1]
            bool found_new = false;
            for (int k = 2; k < c->size; k++) {
                if (solver_lit_value(s, c->lits[k]) != VAL_FALSE) {
                    c->lits[0] = c->lits[k];
                    c->lits[k] = false_lit;
                    watch_list_add(&s->watches[c->lits[0]], w.clause_id, second);
                    found_new = true;
                    break;
                }
            }
            
            if (found_new) {
                i++;
                continue;
            }
            
            // Заміни немає
            wl->data[j++] = w;
            i++;
            
            if (solver_lit_value(s, second) == VAL_FALSE) {
                // Конфлікт!
                while (i < wl->size) {
                    wl->data[j++] = wl->data[i++];
                }
                wl->size = j;
                if (conflict_clause_out) *conflict_clause_out = w.clause_id;
                return false;
            } else {
                // Одиничне поширення!
                solver_enqueue(s, second);
            }
        }
        wl->size = j;
    }
    return true;
}

void solver_backtrack(Solver* s, int target_level) {
    while (s->trail_size > 0) {
        Literal lit = s->trail[s->trail_size - 1];
        Var v = LIT_VAR(lit);
        if (s->assign_levels[v] <= target_level) break;
        
        s->values[v] = VAL_UNASSIGNED;
        s->assign_levels[v] = 0;
        s->trail_size--;
    }
    s->trail_head = s->trail_size;
    s->current_level = target_level;
}

int main(void) {
    Solver* s = solver_create(4);
    
    // (x1 v x2 v x3)
    Literal c1[] = { LIT_MAKE(1, false), LIT_MAKE(2, false), LIT_MAKE(3, false) };
    add_clause(s, c1, 3);
    
    // (¬x1 v x4)
    Literal c2[] = { LIT_MAKE(1, true), LIT_MAKE(4, false) };
    add_clause(s, c2, 2);
    
    // Прийняття рішення: x1 := 1 (True)
    s->current_level = 1;
    solver_enqueue(s, LIT_MAKE(1, false));
    
    int conflict_cid = -1;
    bool ok = solver_propagate(s, &conflict_cid);
    
    printf("BCP Result: %s\n", ok ? "SUCCESS" : "CONFLICT");
    printf("Value x4: %d\n", s->values[4]);
    
    // Безвитратний бектрекінг
    solver_backtrack(s, 0);
    printf("After backtrack Value x1: %d, x4: %d\n", s->values[1], s->values[4]);
    
    solver_free(s);
    return 0;
}
