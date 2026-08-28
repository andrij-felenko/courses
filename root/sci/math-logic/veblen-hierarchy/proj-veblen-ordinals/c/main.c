#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <assert.h>

/* Типи вузлів синтаксичного дерева ординалу */
typedef enum {
    ORD_ZERO,      /* 0 */
    ORD_FINITE,    /* Натуральне число k > 0 */
    ORD_ADD,       /* Сума A + B (де A >= B) */
    ORD_VEBLEN     /* Функція Веблена phi(gamma, beta) */
} OrdinalKind;

typedef struct OrdinalNode OrdinalNode;

struct OrdinalNode {
    OrdinalKind kind;
    unsigned long long value; /* Для ORD_FINITE */
    OrdinalNode* left;        /* Для ADD: лівий доданок; для VEBLEN: gamma */
    OrdinalNode* right;       /* Для ADD: правий доданок; для VEBLEN: beta */
};

/* Створення базових вузлів */
OrdinalNode* ord_zero(void) {
    OrdinalNode* n = (OrdinalNode*)calloc(1, sizeof(OrdinalNode));
    n->kind = ORD_ZERO;
    return n;
}

OrdinalNode* ord_finite(unsigned long long val) {
    if (val == 0) return ord_zero();
    OrdinalNode* n = (OrdinalNode*)calloc(1, sizeof(OrdinalNode));
    n->kind = ORD_FINITE;
    n->value = val;
    return n;
}

/* Глибоке копіювання дерева */
OrdinalNode* ord_clone(const OrdinalNode* src) {
    if (!src) return NULL;
    OrdinalNode* n = (OrdinalNode*)calloc(1, sizeof(OrdinalNode));
    n->kind = src->kind;
    n->value = src->value;
    n->left = ord_clone(src->left);
    n->right = ord_clone(src->right);
    return n;
}

/* Рекурсивне звільнення пам'яті */
void ord_free(OrdinalNode* n) {
    if (!n) return;
    ord_free(n->left);
    ord_free(n->right);
    free(n);
}

/* Попереднє оголошення функції порівняння: повертає -1 (a < b), 0 (a == b), 1 (a > b) */
int ord_cmp(const OrdinalNode* a, const OrdinalNode* b);

/* Допоміжні перевірки */
bool ord_is_zero(const OrdinalNode* n) {
    return !n || n->kind == ORD_ZERO;
}

bool ord_is_principal(const OrdinalNode* n) {
    return n && n->kind == ORD_VEBLEN;
}

/* Порівняння двох адитивно головних функцій Веблена phi(g1, b1) та phi(g2, b2) */
static int ord_cmp_veblen(const OrdinalNode* a, const OrdinalNode* b) {
    assert(a->kind == ORD_VEBLEN && b->kind == ORD_VEBLEN);
    
    int g_cmp = ord_cmp(a->left, b->left);
    if (g_cmp == 0) {
        return ord_cmp(a->right, b->right);
    } else if (g_cmp < 0) {
        /* a->gamma < b->gamma: A < B <=> beta_A < B */
        int cmp_b = ord_cmp(a->right, b);
        return (cmp_b < 0) ? -1 : 1;
    } else {
        /* a->gamma > b->gamma: A < B <=> A <= beta_B */
        int cmp_a = ord_cmp(a, b->right);
        return (cmp_a <= 0) ? -1 : 1;
    }
}

int ord_cmp(const OrdinalNode* a, const OrdinalNode* b) {
    if (a == b) return 0;
    if (ord_is_zero(a) && ord_is_zero(b)) return 0;
    if (ord_is_zero(a)) return -1;
    if (ord_is_zero(b)) return 1;

    if (a->kind == ORD_FINITE && b->kind == ORD_FINITE) {
        if (a->value < b->value) return -1;
        if (a->value > b->value) return 1;
        return 0;
    }
    if (a->kind == ORD_FINITE) return -1; /* Скінченне < трансфінітне */
    if (b->kind == ORD_FINITE) return 1;

    if (a->kind == ORD_VEBLEN && b->kind == ORD_VEBLEN) {
        return ord_cmp_veblen(a, b);
    }

    /* Розбір сум: порівнюємо старші адитивні члени */
    const OrdinalNode* a_head = (a->kind == ORD_ADD) ? a->left : a;
    const OrdinalNode* b_head = (b->kind == ORD_ADD) ? b->left : b;

    int head_cmp = ord_cmp(a_head, b_head);
    if (head_cmp != 0) return head_cmp;

    /* Старші члени рівні: порівнюємо хвости */
    const OrdinalNode* a_tail = (a->kind == ORD_ADD) ? a->right : NULL;
    const OrdinalNode* b_tail = (b->kind == ORD_ADD) ? b->right : NULL;

    return ord_cmp(a_tail, b_tail);
}

/* Нормалізований конструктор функції Веблена phi(gamma, beta) */
OrdinalNode* ord_veblen(OrdinalNode* gamma, OrdinalNode* beta) {
    OrdinalNode* n = (OrdinalNode*)calloc(1, sizeof(OrdinalNode));
    n->kind = ORD_VEBLEN;
    n->left = gamma;
    n->right = beta;
    return n;
}

/* Адитивна композиція (додавання Кантора з поглинанням менших членів зліва) */
OrdinalNode* ord_add(OrdinalNode* a, OrdinalNode* b) {
    if (ord_is_zero(a)) { ord_free(a); return b; }
    if (ord_is_zero(b)) { ord_free(b); return a; }

    /* Якщо обидва скінченні */
    if (a->kind == ORD_FINITE && b->kind == ORD_FINITE) {
        unsigned long long sum = a->value + b->value;
        ord_free(a);
        ord_free(b);
        return ord_finite(sum);
    }

    /* Визначаємо головний член правого доданка */
    const OrdinalNode* b_lead = (b->kind == ORD_ADD) ? b->left : b;

    /* Якщо додаємо скінченне до нескінченного зліва (1 + omega = omega) */
    if (a->kind == ORD_FINITE && b_lead->kind == ORD_VEBLEN) {
        ord_free(a);
        return b;
    }

    /* Перевіряємо поглинання: якщо a < b_lead, a повністю поглинається */
    if (a->kind == ORD_VEBLEN) {
        if (ord_cmp(a, b_lead) < 0) {
            ord_free(a);
            return b;
        }
    } else if (a->kind == ORD_ADD) {
        /* Рекурсивно перевіряємо поглинання у хвості суми */
        if (ord_cmp(a->left, b_lead) < 0) {
            ord_free(a);
            return b;
        }
        /* Збираємо суму: a->left + (a->right + b) */
        OrdinalNode* new_tail = ord_add(a->right, b);
        a->right = new_tail;
        return a;
    }

    OrdinalNode* res = (OrdinalNode*)calloc(1, sizeof(OrdinalNode));
    res->kind = ORD_ADD;
    res->left = a;
    res->right = b;
    return res;
}

/* Форматування ординалу у зрозумілий рядок */
void ord_print_to_buf(const OrdinalNode* n, char* buf, size_t max_len) {
    if (!n || n->kind == ORD_ZERO) {
        snprintf(buf, max_len, "0");
        return;
    }
    if (n->kind == ORD_FINITE) {
        snprintf(buf, max_len, "%llu", n->value);
        return;
    }
    if (n->kind == ORD_VEBLEN) {
        char g_buf[128], b_buf[128];
        ord_print_to_buf(n->left, g_buf, sizeof(g_buf));
        ord_print_to_buf(n->right, b_buf, sizeof(b_buf));

        /* Спеціальні випадки для красивого друку */
        if (n->left->kind == ORD_ZERO) {
            if (n->right->kind == ORD_ZERO) {
                snprintf(buf, max_len, "1");
            } else if (n->right->kind == ORD_FINITE && n->right->value == 1) {
                snprintf(buf, max_len, "w");
            } else {
                snprintf(buf, max_len, "w^(%s)", b_buf);
            }
        } else if (n->left->kind == ORD_FINITE && n->left->value == 1) {
            snprintf(buf, max_len, "eps(%s)", b_buf);
        } else if (n->left->kind == ORD_FINITE && n->left->value == 2) {
            snprintf(buf, max_len, "zeta(%s)", b_buf);
        } else {
            snprintf(buf, max_len, "phi(%s, %s)", g_buf, b_buf);
        }
        return;
    }
    if (n->kind == ORD_ADD) {
        char l_buf[256], r_buf[256];
        ord_print_to_buf(n->left, l_buf, sizeof(l_buf));
        ord_print_to_buf(n->right, r_buf, sizeof(r_buf));
        snprintf(buf, max_len, "%s + %s", l_buf, r_buf);
        return;
    }
}

/* Канонічні ординали для тестування */
OrdinalNode* ord_omega(void) {
    return ord_veblen(ord_zero(), ord_finite(1));
}

OrdinalNode* ord_epsilon0(void) {
    return ord_veblen(ord_finite(1), ord_zero());
}

OrdinalNode* ord_zeta0(void) {
    return ord_veblen(ord_finite(2), ord_zero());
}

int main(void) {
    printf("=== Демонстрація синтаксичного рушія ординалів Веблена (C) ===\n");

    OrdinalNode* zero = ord_zero();
    OrdinalNode* one = ord_finite(1);
    OrdinalNode* w = ord_omega();
    OrdinalNode* w2 = ord_veblen(ord_zero(), ord_finite(2)); /* w^2 */
    OrdinalNode* eps0 = ord_epsilon0();
    OrdinalNode* eps1 = ord_veblen(ord_finite(1), ord_finite(1));
    OrdinalNode* zet0 = ord_zeta0();

    char buf[256];

    ord_print_to_buf(w, buf, sizeof(buf));
    printf("Ординал w: %s\n", buf);

    ord_print_to_buf(eps0, buf, sizeof(buf));
    printf("Ординал eps0: %s\n", buf);

    ord_print_to_buf(zet0, buf, sizeof(buf));
    printf("Ординал zeta0: %s\n", buf);

    /* Перевірка строгого впорядкування */
    assert(ord_cmp(zero, one) < 0);
    assert(ord_cmp(one, w) < 0);
    assert(ord_cmp(w, w2) < 0);
    assert(ord_cmp(w2, eps0) < 0);
    assert(ord_cmp(eps0, eps1) < 0);
    assert(ord_cmp(eps1, zet0) < 0);

    /* Тест на непереставність та поглинання: 1 + w == w */
    OrdinalNode* sum_1_w = ord_add(ord_finite(1), ord_clone(w));
    ord_print_to_buf(sum_1_w, buf, sizeof(buf));
    printf("1 + w = %s\n", buf);
    assert(ord_cmp(sum_1_w, w) == 0);

    /* w + 1 > w */
    OrdinalNode* sum_w_1 = ord_add(ord_clone(w), ord_finite(1));
    ord_print_to_buf(sum_w_1, buf, sizeof(buf));
    printf("w + 1 = %s\n", buf);
    assert(ord_cmp(sum_w_1, w) > 0);

    printf("Усі перевірки впорядкування успішно пройдено!\n");

    ord_free(zero);
    ord_free(one);
    ord_free(w);
    ord_free(w2);
    ord_free(eps0);
    ord_free(eps1);
    ord_free(zet0);
    ord_free(sum_1_w);
    ord_free(sum_w_1);

    return 0;
}
