#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* Пошук елемента більшості у масиві цілих чисел */
bool boyer_moore_majority(const int32_t *data, size_t size, int32_t *out_majority) {
    if (data == NULL || size == 0 || out_majority == NULL) {
        return false;
    }

    int32_t candidate = 0;
    size_t count = 0;

    /* Етап 1: Визначення кандидата */
    for (size_t i = 0; i < size; ++i) {
        if (count == 0) {
            candidate = data[i];
            count = 1;
        } else if (data[i] == candidate) {
            count++;
        } else {
            count--;
        }
    }

    if (count == 0) {
        return false;
    }

    /* Етап 2: Верифікація частоти знайденого кандидата */
    size_t actual_frequency = 0;
    for (size_t i = 0; i < size; ++i) {
        if (data[i] == candidate) {
            actual_frequency++;
        }
    }

    if (actual_frequency > size / 2) {
        *out_majority = candidate;
        return true;
    }

    return false;
}
