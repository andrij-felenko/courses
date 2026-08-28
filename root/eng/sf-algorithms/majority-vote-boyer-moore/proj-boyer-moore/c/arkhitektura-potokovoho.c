#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

typedef struct {
    int32_t candidate;
    size_t count;
} MajorityVoteState;

/* Ініціалізація стану потокового акумулятора */
void majority_state_init(MajorityVoteState *state) {
    state->candidate = 0;
    state->count = 0;
}

/* Однопрохідне потокове оновлення стану для нового елемента */
void majority_state_update(MajorityVoteState *state, int32_t x) {
    if (state->count == 0) {
        state->candidate = x;
        state->count = 1;
    } else if (state->candidate == x) {
        state->count++;
    } else {
        state->count--;
    }
}

/* Повний двопрохідний алгоритм із верифікацією */
bool find_majority_element(const int32_t *data, size_t size, int32_t *out_majority) {
    if (data == NULL || size == 0 || out_majority == NULL) {
        return false;
    }

    MajorityVoteState state;
    majority_state_init(&state);

    /* Прохід 1: Знаходження потенційного кандидата */
    for (size_t i = 0; i < size; ++i) {
        majority_state_update(&state, data[i]);
    }

    /* Якщо лічильник дорівнює нулю, більшості точно немає */
    if (state.count == 0) {
        return false;
    }

    /* Прохід 2: Точний підрахунок частоти кандидата */
    size_t actual_count = 0;
    for (size_t i = 0; i < size; ++i) {
        if (data[i] == state.candidate) {
            actual_count++;
        }
    }

    if (actual_count > size / 2) {
        *out_majority = state.candidate;
        return true;
    }

    return false;
}
