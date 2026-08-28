#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

typedef enum {
    CARD_FINITE,
    CARD_ALEPH,
    CARD_BETH
} CardinalKind;

typedef struct {
    CardinalKind kind;
    uint64_t index; /* числове значення для FINITE, індекс для ALEPH/BETH */
} Cardinal;

static inline Cardinal make_finite(uint64_t n) {
    return (Cardinal){.kind = CARD_FINITE, .index = n};
}

static inline Cardinal make_aleph(uint64_t idx) {
    return (Cardinal){.kind = CARD_ALEPH, .index = idx};
}

static inline Cardinal make_beth(uint64_t idx) {
    return (Cardinal){.kind = CARD_BETH, .index = idx};
}

static inline Cardinal make_continuum(void) {
    return make_beth(1);
}

/* Порівняння кардиналів: -1 (a < b), 0 (a == b), 1 (a > b) */
int compare_cardinals(Cardinal a, Cardinal b) {
    if (a.kind == CARD_FINITE && b.kind == CARD_FINITE) {
        if (a.index < b.index) return -1;
        if (a.index > b.index) return 1;
        return 0;
    }
    if (a.kind == CARD_FINITE) return -1;
    if (b.kind == CARD_FINITE) return 1;

    /* ℵ₀ тотожний ℶ₀ */
    if (a.index == 0 && b.index == 0) return 0;

    if (a.kind == b.kind) {
        if (a.index < b.index) return -1;
        if (a.index > b.index) return 1;
        return 0;
    }

    if (a.kind == CARD_ALEPH && b.kind == CARD_BETH) {
        return -1;
    }
    return 1;
}

/* κ + λ = max(κ, λ) для трансфінітних */
Cardinal add_cardinals(Cardinal a, Cardinal b) {
    if (a.kind == CARD_FINITE && b.kind == CARD_FINITE) {
        return make_finite(a.index + b.index);
    }
    return (compare_cardinals(a, b) >= 0) ? a : b;
}

/* κ · λ = max(κ, λ) для трансфінітних ненульових */
Cardinal mul_cardinals(Cardinal a, Cardinal b) {
    if ((a.kind == CARD_FINITE && a.index == 0) ||
        (b.kind == CARD_FINITE && b.index == 0)) {
        return make_finite(0);
    }
    if (a.kind == CARD_FINITE && b.kind == CARD_FINITE) {
        return make_finite(a.index * b.index);
    }
    return (compare_cardinals(a, b) >= 0) ? a : b;
}

/* Піднесення до степеня κ^λ */
Cardinal pow_cardinals(Cardinal base, Cardinal exp) {
    if (exp.kind == CARD_FINITE && exp.index == 0) return make_finite(1);
    if (base.kind == CARD_FINITE && base.index == 0) return make_finite(0);
    if (base.kind == CARD_FINITE && base.index == 1) return make_finite(1);

    if (base.kind == CARD_FINITE && exp.kind == CARD_FINITE) {
        uint64_t res = 1;
        for (uint64_t i = 0; i < exp.index; ++i) res *= base.index;
        return make_finite(res);
    }

    /* 2^ℵ_α = ℶ_(α+1), 2^ℶ_β = ℶ_(β+1) */
    if (base.kind == CARD_FINITE && base.index >= 2) {
        return make_beth(exp.index + 1);
    }

    if (compare_cardinals(base, exp) <= 0) {
        return make_beth(exp.index + 1);
    }

    return base;
}
