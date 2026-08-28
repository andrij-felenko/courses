#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <assert.h>

#define MAX_ARGS 4
#define MAX_NAME 16
#define MAX_VARS 32
#define MAX_RULES 64
#define MAX_PAIRS 256

typedef enum { TERM_VAR, TERM_FN } TermKind;

typedef struct Term {
    TermKind kind;
    char name[MAX_NAME];
    int arity;
    struct Term* args[MAX_ARGS];
} Term;

typedef struct {
    char var[MAX_NAME];
    Term* term;
} SubstEntry;

typedef struct {
    SubstEntry entries[MAX_VARS];
    int count;
} Substitution;

typedef struct {
    Term* lhs;
    Term* rhs;
} Rule;

// Створення та клонування термів
Term* make_var(const char* name) {
    Term* t = (Term*)malloc(sizeof(Term));
    t->kind = TERM_VAR;
    strncpy(t->name, name, MAX_NAME - 1);
    t->name[MAX_NAME - 1] = '\0';
    t->arity = 0;
    return t;
}

Term* make_fn(const char* name, int arity, Term** args) {
    Term* t = (Term*)malloc(sizeof(Term));
    t->kind = TERM_FN;
    strncpy(t->name, name, MAX_NAME - 1);
    t->name[MAX_NAME - 1] = '\0';
    t->arity = arity;
    for (int i = 0; i < arity; ++i) t->args[i] = args[i];
    return t;
}

Term* clone_term(const Term* t) {
    if (!t) return NULL;
    if (t->kind == TERM_VAR) return make_var(t->name);
    Term* new_args[MAX_ARGS];
    for (int i = 0; i < t->arity; ++i) new_args[i] = clone_term(t->args[i]);
    return make_fn(t->name, t->arity, new_args);
}

void free_term(Term* t) {
    if (!t) return;
    for (int i = 0; i < t->arity; ++i) free_term(t->args[i]);
    free(t);
}

void print_term(const Term* t) {
    if (t->kind == TERM_VAR) {
        printf("%s", t->name);
    } else if (t->arity == 0) {
        printf("%s", t->name);
    } else if (t->arity == 2 && strcmp(t->name, "*") == 0) {
        printf("(");
        print_term(t->args[0]);
        printf(" * ");
        print_term(t->args[1]);
        printf(")");
    } else {
        printf("%s(", t->name);
        for (int i = 0; i < t->arity; ++i) {
            if (i > 0) printf(", ");
            print_term(t->args[i]);
        }
        printf(")");
    }
}

// Порівняння та перевірка входження змінних
bool terms_equal(const Term* a, const Term* b) {
    if (a->kind != b->kind || strcmp(a->name, b->name) != 0 || a->arity != b->arity) return false;
    for (int i = 0; i < a->arity; ++i) {
        if (!terms_equal(a->args[i], b->args[i])) return false;
    }
    return true;
}

bool contains_var(const Term* t, const char* var_name) {
    if (t->kind == TERM_VAR) return strcmp(t->name, var_name) == 0;
    for (int i = 0; i < t->arity; ++i) {
        if (contains_var(t->args[i], var_name)) return true;
    }
    return false;
}

Term* apply_subst(const Term* t, const Substitution* s) {
    if (t->kind == TERM_VAR) {
        for (int i = 0; i < s->count; ++i) {
            if (strcmp(s->entries[i].var, t->name) == 0) {
                return apply_subst(s->entries[i].term, s);
            }
        }
        return make_var(t->name);
    }
    Term* new_args[MAX_ARGS];
    for (int i = 0; i < t->arity; ++i) new_args[i] = apply_subst(t->args[i], s);
    return make_fn(t->name, t->arity, new_args);
}

// Уніфікація Робінсона
bool unify(const Term* s, const Term* t, Substitution* subst) {
    Term* s_sub = apply_subst(s, subst);
    Term* t_sub = apply_subst(t, subst);

    if (terms_equal(s_sub, t_sub)) {
        free_term(s_sub); free_term(t_sub);
        return true;
    }
    if (s_sub->kind == TERM_VAR) {
        if (contains_var(t_sub, s_sub->name)) {
            free_term(s_sub); free_term(t_sub);
            return false;
        }
        strncpy(subst->entries[subst->count].var, s_sub->name, MAX_NAME - 1);
        subst->entries[subst->count].term = clone_term(t_sub);
        subst->count++;
        free_term(s_sub); free_term(t_sub);
        return true;
    }
    if (t_sub->kind == TERM_VAR) {
        if (contains_var(s_sub, t_sub->name)) {
            free_term(s_sub); free_term(t_sub);
            return false;
        }
        strncpy(subst->entries[subst->count].var, t_sub->name, MAX_NAME - 1);
        subst->entries[subst->count].term = clone_term(s_sub);
        subst->count++;
        free_term(s_sub); free_term(t_sub);
        return true;
    }
    if (strcmp(s_sub->name, t_sub->name) != 0 || s_sub->arity != t_sub->arity) {
        free_term(s_sub); free_term(t_sub);
        return false;
    }
    for (int i = 0; i < s_sub->arity; ++i) {
        if (!unify(s_sub->args[i], t_sub->args[i], subst)) {
            free_term(s_sub); free_term(t_sub);
            return false;
        }
    }
    free_term(s_sub); free_term(t_sub);
    return true;
}

// Зіставлення за зразком
bool match_pattern(const Term* pat, const Term* tgt, Substitution* subst) {
    if (pat->kind == TERM_VAR) {
        for (int i = 0; i < subst->count; ++i) {
            if (strcmp(subst->entries[i].var, pat->name) == 0) {
                return terms_equal(subst->entries[i].term, tgt);
            }
        }
        strncpy(subst->entries[subst->count].var, pat->name, MAX_NAME - 1);
        subst->entries[subst->count].term = clone_term(tgt);
        subst->count++;
        return true;
    }
    if (tgt->kind == TERM_VAR || strcmp(pat->name, tgt->name) != 0 || pat->arity != tgt->arity) return false;
    for (int i = 0; i < pat->arity; ++i) {
        if (!match_pattern(pat->args[i], tgt->args[i], subst)) return false;
    }
    return true;
}

// Порядок LPO
int symbol_prec(const char* name) {
    if (strcmp(name, "i") == 0) return 3;
    if (strcmp(name, "*") == 0) return 2;
    if (strcmp(name, "e") == 0) return 1;
    return 0;
}

bool lpo_greater(const Term* s, const Term* t) {
    if (t->kind == TERM_VAR) return contains_var(s, t->name) && !terms_equal(s, t);
    if (s->kind == TERM_VAR) return false;

    for (int i = 0; i < s->arity; ++i) {
        if (terms_equal(s->args[i], t) || lpo_greater(s->args[i], t)) return true;
    }

    int ps = symbol_prec(s->name), pt = symbol_prec(t->name);
    for (int j = 0; j < t->arity; ++j) {
        if (!lpo_greater(s, t->args[j])) return false;
    }
    if (ps > pt) return true;
    if (ps == pt && strcmp(s->name, t->name) == 0 && s->arity == t->arity) {
        for (int i = 0; i < s->arity; ++i) {
            if (terms_equal(s->args[i], t->args[i])) continue;
            return lpo_greater(s->args[i], t->args[i]);
        }
    }
    return false;
}

// Нормалізація та поповнення
Term* rewrite_step(const Term* t, const Rule* rules, int rule_count) {
    if (t->kind == TERM_FN) {
        for (int i = 0; i < t->arity; ++i) {
            Term* red = rewrite_step(t->args[i], rules, rule_count);
            if (!terms_equal(red, t->args[i])) {
                Term* new_args[MAX_ARGS];
                for (int j = 0; j < t->arity; ++j) new_args[j] = (i == j) ? red : clone_term(t->args[j]);
                return make_fn(t->name, t->arity, new_args);
            }
            free_term(red);
        }
    }
    for (int r = 0; r < rule_count; ++r) {
        Substitution s = { .count = 0 };
        if (match_pattern(rules[r].lhs, t, &s)) {
            Term* res = apply_subst(rules[r].rhs, &s);
            for (int i = 0; i < s.count; ++i) free_term(s.entries[i].term);
            return res;
        }
    }
    return clone_term(t);
}

Term* normalize(Term* t, const Rule* rules, int rule_count) {
    while (true) {
        Term* nxt = rewrite_step(t, rules, rule_count);
        if (terms_equal(nxt, t)) { free_term(nxt); break; }
        free_term(t);
        t = nxt;
    }
    return t;
}

int main(void) {
    Term* x = make_var("x");
    Term* y = make_var("y");
    Term* z = make_var("z");
    Term* e = make_fn("e", 0, NULL);

    Term* a1[2] = { e, x };
    Term* ax1_l = make_fn("*", 2, a1);
    Term* ax1_r = make_var("x");

    printf("=== Рушій переписування термів на C: Демонстрація LPO ===\n");
    printf("Аксіома 1: ");
    print_term(ax1_l);
    printf(" = ");
    print_term(ax1_r);
    printf("\nЧи ax1_l > ax1_r за LPO? %s\n", lpo_greater(ax1_l, ax1_r) ? "ТАК" : "НІ");

    free_term(ax1_l); free_term(ax1_r);
    free_term(y); free_term(z);
    return 0;
}
