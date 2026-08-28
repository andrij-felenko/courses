static void ensure_temp_capacity(TimSortState *state, size_t needed) {
    if (state->temp_capacity < needed) {
        state->temp_buf = (int *)realloc(state->temp_buf, needed * sizeof(int));
        state->temp_capacity = needed;
    }
}

static void merge_lo(TimSortState *state, size_t base_a, size_t len_a, size_t base_b, size_t len_b) {
    ensure_temp_capacity(state, len_a);
    memcpy(state->temp_buf, &state->array[base_a], len_a * sizeof(int));

    size_t cursor_a = 0;
    size_t cursor_b = base_b;
    size_t dest = base_a;
    size_t min_gallop = state->min_gallop;

    while (cursor_a < len_a && cursor_b < base_b + len_b) {
        size_t count_a = 0;
        size_t count_b = 0;

        // Покроковий режим
        do {
            if (state->array[cursor_b] < state->temp_buf[cursor_a]) {
                state->array[dest++] = state->array[cursor_b++];
                count_b++;
                count_a = 0;
                if (cursor_b == base_b + len_b) goto outer_lo;
            } else {
                state->array[dest++] = state->temp_buf[cursor_a++];
                count_a++;
                count_b = 0;
                if (cursor_a == len_a) goto outer_lo;
            }
        } while ((count_a | count_b) < min_gallop);

        // Режим галопу
        do {
            count_a = gallop_right(state->array[cursor_b], state->temp_buf, cursor_a, len_a - cursor_a, 0);
            if (count_a > 0) {
                memcpy(&state->array[dest], &state->temp_buf[cursor_a], count_a * sizeof(int));
                dest += count_a;
                cursor_a += count_a;
                if (cursor_a == len_a) goto outer_lo;
            }
            state->array[dest++] = state->array[cursor_b++];
            if (cursor_b == base_b + len_b) goto outer_lo;

            count_b = gallop_left(state->temp_buf[cursor_a], state->array, cursor_b, base_b + len_b - cursor_b, 0);
            if (count_b > 0) {
                memmove(&state->array[dest], &state->array[cursor_b], count_b * sizeof(int));
                dest += count_b;
                cursor_b += count_b;
                if (cursor_b == base_b + len_b) goto outer_lo;
            }
            state->array[dest++] = state->temp_buf[cursor_a++];
            if (cursor_a == len_a) goto outer_lo;

            min_gallop--;
        } while (count_a >= MIN_GALLOP_DEFAULT || count_b >= MIN_GALLOP_DEFAULT);

        if (min_gallop < 1) min_gallop = 1;
        min_gallop += 2; // Штраф за вихід із галопу
    }

outer_lo:
    state->min_gallop = (min_gallop < 1) ? 1 : min_gallop;
    if (cursor_a < len_a) {
        memcpy(&state->array[dest], &state->temp_buf[cursor_a], (len_a - cursor_a) * sizeof(int));
    }
}

static void merge_hi(TimSortState *state, size_t base_a, size_t len_a, size_t base_b, size_t len_b) {
    ensure_temp_capacity(state, len_b);
    memcpy(state->temp_buf, &state->array[base_b], len_b * sizeof(int));

    size_t cursor_a = base_a + len_a - 1;
    size_t cursor_b = len_b - 1;
    size_t dest = base_b + len_b - 1;
    size_t min_gallop = state->min_gallop;

    while (len_a > 0 && len_b > 0) {
        size_t count_a = 0;
        size_t count_b = 0;

        do {
            if (state->temp_buf[cursor_b] < state->array[cursor_a]) {
                state->array[dest--] = state->array[cursor_a--];
                len_a--;
                count_a++;
                count_b = 0;
                if (len_a == 0) goto outer_hi;
            } else {
                state->array[dest--] = state->temp_buf[cursor_b--];
                len_b--;
                count_b++;
                count_a = 0;
                if (len_b == 0) goto outer_hi;
            }
        } while ((count_a | count_b) < min_gallop);

        do {
            count_a = len_a - gallop_right(state->temp_buf[cursor_b], state->array, base_a, len_a, len_a - 1);
            if (count_a > 0) {
                dest -= count_a;
                cursor_a -= count_a;
                len_a -= count_a;
                memmove(&state->array[dest + 1], &state->array[cursor_a + 1], count_a * sizeof(int));
                if (len_a == 0) goto outer_hi;
            }
            state->array[dest--] = state->temp_buf[cursor_b--];
            len_b--;
            if (len_b == 0) goto outer_hi;

            count_b = len_b - gallop_left(state->array[cursor_a], state->temp_buf, 0, len_b, len_b - 1);
            if (count_b > 0) {
                dest -= count_b;
                cursor_b -= count_b;
                len_b -= count_b;
                memcpy(&state->array[dest + 1], &state->temp_buf[cursor_b + 1], count_b * sizeof(int));
                if (len_b == 0) goto outer_hi;
            }
            state->array[dest--] = state->array[cursor_a--];
            len_a--;
            if (len_a == 0) goto outer_hi;

            min_gallop--;
        } while (count_a >= MIN_GALLOP_DEFAULT || count_b >= MIN_GALLOP_DEFAULT);

        if (min_gallop < 1) min_gallop = 1;
        min_gallop += 2;
    }

outer_hi:
    state->min_gallop = (min_gallop < 1) ? 1 : min_gallop;
    if (len_b > 0) {
        memcpy(&state->array[dest - len_b + 1], state->temp_buf, len_b * sizeof(int));
    }
}

static void merge_at(TimSortState *state, size_t i) {
    size_t base_a = state->stack[i].start;
    size_t len_a = state->stack[i].len;
    size_t base_b = state->stack[i + 1].start;
    size_t len_b = state->stack[i + 1].len;

    state->stack[i].len = len_a + len_b;
    if (i == state->stack_size - 3) {
        state->stack[i + 1] = state->stack[i + 2];
    }
    state->stack_size--;

    size_t k = gallop_right(state->array[base_b], state->array, base_a, len_a, 0);
    base_a += k;
    len_a -= k;
    if (len_a == 0) return;

    len_b = gallop_left(state->array[base_a + len_a - 1], state->array, base_b, len_b, len_b - 1);
    if (len_b == 0) return;

    if (len_a <= len_b) {
        merge_lo(state, base_a, len_a, base_b, len_b);
    } else {
        merge_hi(state, base_a, len_a, base_b, len_b);
    }
}
