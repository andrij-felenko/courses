#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#define MG_K 3
#define MG_SLOTS (MG_K - 1)

typedef struct {
    int32_t candidate[MG_SLOTS];
    size_t count[MG_SLOTS];
} MisraGries3State;

void mg3_init(MisraGries3State *state) {
    for (size_t i = 0; i < MG_SLOTS; ++i) {
        state->candidate[i] = 0;
        state->count[i] = 0;
    }
}

void mg3_update(MisraGries3State *state, int32_t x) {
    /* 1. Перевірка чи елемент вже є серед кандидатів */
    for (size_t i = 0; i < MG_SLOTS; ++i) {
        if (state->count[i] > 0 && state->candidate[i] == x) {
            state->count[i]++;
            return;
        }
    }

    /* 2. Пошук порожнього слота */
    for (size_t i = 0; i < MG_SLOTS; ++i) {
        if (state->count[i] == 0) {
            state->candidate[i] = x;
            state->count[i] = 1;
            return;
        }
    }

    /* 3. Всі слоти зайняті та елемент новий: групове скорочення */
    for (size_t i = 0; i < MG_SLOTS; ++i) {
        state->count[i]--;
    }
}
