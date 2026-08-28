#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

/* Типи вузлів синтаксичного дерева термів Пеано */
typedef enum {
    TERM_ZERO,
    TERM_SUCC,
    TERM_ADD,
    TERM_MUL,
    TERM_VAR
} TermType;

typedef struct Term {
    TermType type;
    union {
        char var_name[16];           /* Для TERM_VAR */
        struct Term* child;          /* Для TERM_SUCC */
        struct {                     /* Для TERM_ADD та TERM_MUL */
            struct Term* left;
            struct Term* right;
        } binary;
    } data;
} Term;

/* Конструктори вузлів AST */
Term* create_zero(void) {
    Term* t = (Term*)malloc(sizeof(Term));
    if (!t) exit(1);
    t->type = TERM_ZERO;
    return t;
}

Term* create_var(const char* name) {
    Term* t = (Term*)malloc(sizeof(Term));
    if (!t) exit(1);
    t->type = TERM_VAR;
    strncpy(t->data.var_name, name, 15);
    t->data.var_name[15] = '\0';
    return t;
}

Term* create_succ(Term* child) {
    Term* t = (Term*)malloc(sizeof(Term));
    if (!t) exit(1);
    t->type = TERM_SUCC;
    t->data.child = child;
    return t;
}

Term* create_add(Term* left, Term* right) {
    Term* t = (Term*)malloc(sizeof(Term));
    if (!t) exit(1);
    t->type = TERM_ADD;
    t->data.binary.left = left;
    t->data.binary.right = right;
    return t;
}

Term* create_mul(Term* left, Term* right) {
    Term* t = (Term*)malloc(sizeof(Term));
    if (!t) exit(1);
    t->type = TERM_MUL;
    t->data.binary.left = left;
    t->data.binary.right = right;
    return t;
}

void free_term(Term* t) {
    if (!t) return;
    if (t->type == TERM_SUCC) {
        free_term(t->data.child);
    } else if (t->type == TERM_ADD || t->type == TERM_MUL) {
        free_term(t->data.binary.left);
        free_term(t->data.binary.right);
    }
    free(t);
}

/* Глибоке копіювання терма */
Term* copy_term(const Term* t) {
    if (!t) return NULL;
    switch (t->type) {
        case TERM_ZERO: return create_zero();
        case TERM_VAR:  return create_var(t->data.var_name);
        case TERM_SUCC: return create_succ(copy_term(t->data.child));
        case TERM_ADD:  return create_add(copy_term(t->data.binary.left), copy_term(t->data.binary.right));
        case TERM_MUL:  return create_mul(copy_term(t->data.binary.left), copy_term(t->data.binary.right));
    }
    return NULL;
}

/* Перевірка синтаксичної рівності двох термів */
bool terms_equal(const Term* a, const Term* b) {
    if (a == b) return true;
    if (!a || !b || a->type != b->type) return false;
    switch (a->type) {
        case TERM_ZERO: return true;
        case TERM_VAR:  return strcmp(a->data.var_name, b->data.var_name) == 0;
        case TERM_SUCC: return terms_equal(a->data.child, b->data.child);
        case TERM_ADD:
        case TERM_MUL:
            return terms_equal(a->data.binary.left, b->data.binary.left) &&
                   terms_equal(a->data.binary.right, b->data.binary.right);
    }
    return false;
}

/* Друк терма у звичній синтаксичній формі */
void print_term(const Term* t) {
    if (!t) return;
    switch (t->type) {
        case TERM_ZERO: printf("0"); break;
        case TERM_VAR:  printf("%s", t->data.var_name); break;
        case TERM_SUCC:
            printf("S(");
            print_term(t->data.child);
            printf(")");
            break;
        case TERM_ADD:
            printf("(");
            print_term(t->data.binary.left);
            printf(" + ");
            print_term(t->data.binary.right);
            printf(")");
            break;
        case TERM_MUL:
            printf("(");
            print_term(t->data.binary.left);
            printf(" · ");
            print_term(t->data.binary.right);
            printf(")");
            break;
    }
}

/* Редукція (спрощення) терма за аксіомами Пеано:
   1. x + 0 -> x
   2. x + S(y) -> S(x + y)
   3. x · 0 -> 0
   4. x · S(y) -> (x · y) + x
*/
Term* reduce_term(Term* t, bool* changed) {
    if (!t) return NULL;

    if (t->type == TERM_SUCC) {
        t->data.child = reduce_term(t->data.child, changed);
        return t;
    }

    if (t->type == TERM_ADD) {
        t->data.binary.left = reduce_term(t->data.binary.left, changed);
        t->data.binary.right = reduce_term(t->data.binary.right, changed);
        
        Term* right = t->data.binary.right;
        /* Аксіома: x + 0 -> x */
        if (right->type == TERM_ZERO) {
            Term* left = t->data.binary.left;
            free(right);
            free(t);
            *changed = true;
            return left;
        }
        /* Аксіома: x + S(y) -> S(x + y) */
        if (right->type == TERM_SUCC) {
            Term* left = t->data.binary.left;
            Term* y = right->data.child;
            Term* new_add = create_add(left, y);
            free(right);
            free(t);
            *changed = true;
            return create_succ(new_add);
        }
    }

    if (t->type == TERM_MUL) {
        t->data.binary.left = reduce_term(t->data.binary.left, changed);
        t->data.binary.right = reduce_term(t->data.binary.right, changed);

        Term* right = t->data.binary.right;
        /* Аксіома: x · 0 -> 0 */
        if (right->type == TERM_ZERO) {
            free_term(t->data.binary.left);
            free(right);
            free(t);
            *changed = true;
            return create_zero();
        }
        /* Аксіома: x · S(y) -> (x · y) + x */
        if (right->type == TERM_SUCC) {
            Term* left = t->data.binary.left;
            Term* y = right->data.child;
            Term* mul_xy = create_mul(copy_term(left), y);
            Term* new_add = create_add(mul_xy, left);
            free(right);
            free(t);
            *changed = true;
            return new_add;
        }
    }

    return t;
}

/* Повне нормалізуюче спрощення терма до нормальної форми Пеано */
Term* normalize(Term* t) {
    bool changed = false;
    do {
        changed = false;
        t = reduce_term(t, &changed);
    } while (changed);
    return t;
}

int main(void) {
    printf("=== Інтерпретатор та редуктор термів арифметики Пеано (C) ===\n\n");

    /* Побудова терма: (x + S(0)) + S(S(0)) */
    Term* x = create_var("x");
    Term* one = create_succ(create_zero());
    Term* two = create_succ(create_succ(create_zero()));
    
    Term* expr = create_add(create_add(x, one), two);

    printf("Початковий терм: ");
    print_term(expr);
    printf("\n");

    expr = normalize(expr);

    printf("Нормалізована форма: ");
    print_term(expr);
    printf("\n\n");

    free_term(expr);
    return 0;
}
