#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include <inttypes.h>

typedef enum {
    CARD_FINITE,
    CARD_ALEPH,
    CARD_BETH
} CardKind;

typedef struct {
    CardKind kind;
    uint64_t val; /* Числове значення для FINITE або індекс для ALEPH/BETH */
} Cardinal;

/* Конструктори кардинальних чисел */
static inline Cardinal card_finite(uint64_t n) {
    return (Cardinal){.kind = CARD_FINITE, .val = n};
}

static inline Cardinal card_aleph(uint64_t idx) {
    return (Cardinal){.kind = CARD_ALEPH, .val = idx};
}

static inline Cardinal card_beth(uint64_t idx) {
    return (Cardinal){.kind = CARD_BETH, .val = idx};
}

static inline Cardinal card_continuum(void) {
    return card_beth(1);
}

/* Тризначне порівняння: -1 (a < b), 0 (a == b), 1 (a > b) */
int cardinal_cmp(Cardinal a, Cardinal b) {
    if (a.kind == CARD_FINITE && b.kind == CARD_FINITE) {
        if (a.val < b.val) return -1;
        if (a.val > b.val) return 1;
        return 0;
    }
    if (a.kind == CARD_FINITE) return -1;
    if (b.kind == CARD_FINITE) return 1;

    /* Спрощення: ℵ_0 тотожний ℶ_0 */
    if (a.val == 0 && b.val == 0) return 0;

    if (a.kind == b.kind) {
        if (a.val < b.val) return -1;
        if (a.val > b.val) return 1;
        return 0;
    }

    /* За теоремою Кантора ℶ_k >= ℵ_k */
    if (a.kind == CARD_ALEPH && b.kind == CARD_BETH) {
        return -1;
    }
    if (a.kind == CARD_BETH && b.kind == CARD_ALEPH) {
        return 1;
    }
    return 0;
}

/* Додавання кардиналів: κ + λ = max(κ, λ) для трансфінітних */
Cardinal cardinal_add(Cardinal a, Cardinal b) {
    if (a.kind == CARD_FINITE && b.kind == CARD_FINITE) {
        return card_finite(a.val + b.val);
    }
    return (cardinal_cmp(a, b) >= 0) ? a : b;
}

/* Множення кардиналів: κ · λ = max(κ, λ) для трансфінітних ненульових */
Cardinal cardinal_mul(Cardinal a, Cardinal b) {
    if (a.kind == CARD_FINITE && a.val == 0) return card_finite(0);
    if (b.kind == CARD_FINITE && b.val == 0) return card_finite(0);
    if (a.kind == CARD_FINITE && b.kind == CARD_FINITE) {
        return card_finite(a.val * b.val);
    }
    return (cardinal_cmp(a, b) >= 0) ? a : b;
}

/* Піднесення до степеня: κ^λ */
Cardinal cardinal_pow(Cardinal base, Cardinal exp) {
    if (exp.kind == CARD_FINITE && exp.val == 0) return card_finite(1);
    if (base.kind == CARD_FINITE && base.val == 0) return card_finite(0);
    if (base.kind == CARD_FINITE && base.val == 1) return card_finite(1);

    if (base.kind == CARD_FINITE && exp.kind == CARD_FINITE) {
        uint64_t res = 1;
        for (uint64_t i = 0; i < exp.val; ++i) res *= base.val;
        return card_finite(res);
    }

    /* n^ℵ_α = ℶ_(α+1) при n >= 2 */
    if (base.kind == CARD_FINITE && base.val >= 2) {
        if (exp.kind == CARD_ALEPH) return card_beth(exp.val + 1);
        if (exp.kind == CARD_BETH)  return card_beth(exp.val + 1);
    }

    /* κ^λ = 2^λ при κ <= λ */
    if (cardinal_cmp(base, exp) <= 0) {
        if (exp.kind == CARD_ALEPH) return card_beth(exp.val + 1);
        if (exp.kind == CARD_BETH)  return card_beth(exp.val + 1);
    }

    return base;
}

void cardinal_print(Cardinal c) {
    switch (c.kind) {
        case CARD_FINITE:
            printf("%" PRIu64, c.val);
            break;
        case CARD_ALEPH:
            printf("Aleph_%" PRIu64, c.val);
            break;
        case CARD_BETH:
            if (c.val == 1) {
                printf("c (Beth_1)");
            } else {
                printf("Beth_%" PRIu64, c.val);
            }
            break;
    }
}

int main(void) {
    Cardinal aleph0 = card_aleph(0);
    Cardinal aleph1 = card_aleph(1);
    Cardinal c = card_continuum();
    Cardinal ten = card_finite(10);
    Cardinal two = card_finite(2);

    printf("1. Aleph_0 + 10 = ");
    cardinal_print(cardinal_add(aleph0, ten));
    printf("\n");

    printf("2. Aleph_0 * Aleph_1 = ");
    cardinal_print(cardinal_mul(aleph0, aleph1));
    printf("\n");

    printf("3. 2 ^ Aleph_0 = ");
    cardinal_print(cardinal_pow(two, aleph0));
    printf("\n");

    printf("4. c ^ Aleph_0 = ");
    cardinal_print(cardinal_pow(c, aleph0));
    printf("\n");

    printf("5. 2 ^ c = ");
    cardinal_print(cardinal_pow(two, c));
    printf("\n");

    return 0;
}
