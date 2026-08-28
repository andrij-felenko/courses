#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_ATTRS 32
#define MAX_FDS   64
#define MAX_KEYS  128

typedef struct {
    char name[32];
} Attribute;

typedef struct {
    uint32_t lhs; /* Детермінант X */
    uint32_t rhs; /* Залежні атрибути Y */
} FuncDep;

typedef struct {
    Attribute attrs[MAX_ATTRS];
    int attr_count;
    FuncDep fds[MAX_FDS];
    int fd_count;
    uint32_t candidate_keys[MAX_KEYS];
    int key_count;
} RelSchema;

/* Обчислення замикання підмножини атрибутів відносно заданих залежностей */
uint32_t compute_closure(uint32_t mask, const FuncDep fds[], int fd_count) {
    uint32_t closure = mask;
    bool changed = true;

    while (changed) {
        changed = false;
        for (int i = 0; i < fd_count; i++) {
            /* Якщо детермінант є підмножиною поточного замикання */
            if ((fds[i].lhs & closure) == fds[i].lhs) {
                uint32_t next = closure | fds[i].rhs;
                if (next != closure) {
                    closure = next;
                    changed = true;
                }
            }
        }
    }
    return closure;
}

/* Пошук усіх мінімальних кандидатних ключів через перебір підмножин */
void find_candidate_keys(RelSchema *schema) {
    schema->key_count = 0;
    uint32_t all_attrs = (1U << schema->attr_count) - 1;

    /* Перебираємо підмножини за зростанням їхнього розміру (кардинальності) */
    for (uint32_t mask = 1; mask <= all_attrs; mask++) {
        /* Якщо підмножина вже містить раніше знайдений кандидатний ключ, вона не є мінімальною */
        bool superset_of_key = false;
        for (int k = 0; k < schema->key_count; k++) {
            if ((schema->candidate_keys[k] & mask) == schema->candidate_keys[k]) {
                superset_of_key = true;
                break;
            }
        }
        if (superset_of_key) continue;

        /* Перевіряємо, чи замикання покриває всі атрибути */
        if (compute_closure(mask, schema->fds, schema->fd_count) == all_attrs) {
            if (schema->key_count < MAX_KEYS) {
                schema->candidate_keys[schema->key_count++] = mask;
            }
        }
    }
}

/* Перевірка належності до нормальних форм */
typedef enum {
    VIOLATES_1NF = 0,
    IS_1NF,
    IS_2NF,
    IS_3NF,
    IS_BCNF
} NormalForm;

NormalForm evaluate_normal_form(const RelSchema *schema, char *reason, size_t rsize) {
    uint32_t all_attrs = (1U << schema->attr_count) - 1;
    uint32_t prime_attrs = 0;

    for (int k = 0; k < schema->key_count; k++) {
        prime_attrs |= schema->candidate_keys[k];
    }
    uint32_t non_prime = all_attrs & ~prime_attrs;

    /* 1. Перевірка 2NF: відсутність часткових залежностей непервинних атрибутів від кандидатних ключів */
    for (int i = 0; i < schema->fd_count; i++) {
        uint32_t lhs = schema->fds[i].lhs;
        uint32_t non_prime_rhs = schema->fds[i].rhs & non_prime;

        if (non_prime_rhs == 0) continue;

        for (int k = 0; k < schema->key_count; k++) {
            uint32_t key = schema->candidate_keys[k];
            /* Якщо lhs є ВЛАСНОЮ підмножиною ключа (lhs ⊂ key) */
            if ((lhs & key) == lhs && lhs != key) {
                snprintf(reason, rsize, "Порушення 2NF: атрибути непервинної частини залежать від частини ключа.");
                return IS_1NF;
            }
        }
    }

    /* 2. Перевірка 3NF та BCNF */
    bool satisfies_bcnf = true;
    for (int i = 0; i < schema->fd_count; i++) {
        uint32_t lhs = schema->fds[i].lhs;
        uint32_t rhs = schema->fds[i].rhs;
        uint32_t non_trivial_rhs = rhs & ~lhs;

        if (non_trivial_rhs == 0) continue; /* Тривіальна залежність */

        /* Чи є lhs суперключем? */
        bool is_superkey = (compute_closure(lhs, schema->fds, schema->fd_count) == all_attrs);

        if (!is_superkey) {
            satisfies_bcnf = false;
            /* Для 3NF кожен атрибут з non_trivial_rhs мусить бути первинним */
            if ((non_trivial_rhs & ~prime_attrs) != 0) {
                snprintf(reason, rsize, "Порушення 3NF: транзитивна залежність на непервинний атрибут.");
                return IS_2NF;
            }
        }
    }

    if (satisfies_bcnf) {
        snprintf(reason, rsize, "Схема перебуває у найвищій нормальній формі Бойса–Кодда (BCNF).");
        return IS_BCNF;
    }

    snprintf(reason, rsize, "Схема перебуває у 3NF (але порушує BCNF через перетин кандидатних ключів).");
    return IS_3NF;
}
