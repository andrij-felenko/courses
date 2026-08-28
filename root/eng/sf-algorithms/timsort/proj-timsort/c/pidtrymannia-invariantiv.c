static void merge_at(TimSortState *state, size_t i);

static void merge_collapse(TimSortState *state) {
    while (state->stack_size > 1) {
        size_t n = state->stack_size - 2;

        if ((n >= 1 && state->stack[n - 1].len <= state->stack[n].len + state->stack[n + 1].len) ||
            (n >= 2 && state->stack[n - 2].len <= state->stack[n - 1].len + state->stack[n].len)) {
            if (state->stack[n - 1].len < state->stack[n + 1].len) {
                n--;
            }
            merge_at(state, n);
        } else if (state->stack[n].len <= state->stack[n + 1].len) {
            merge_at(state, n);
        } else {
            break; // Всі інваріанти задоволено
        }
    }
}

static void merge_force_collapse(TimSortState *state) {
    while (state->stack_size > 1) {
        size_t n = state->stack_size - 2;
        if (n > 0 && state->stack[n - 1].len < state->stack[n + 1].len) {
            n--;
        }
        merge_at(state, n);
    }
}
