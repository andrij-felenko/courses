#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

/* Структура одновимірної розрідженої таблиці для мінімумів (RMQ) */
typedef struct {
    size_t n;            /* Кількість елементів у вихідному масиві */
    size_t levels;       /* Кількість рівнів: floor(log2(n)) + 1 */
    int32_t *data;       /* Плоский масив розміру levels * n */
} sparse_table_t;

/* Обчислення floor(log2(x)) через апаратну інструкцію CLZ */
static inline size_t st_log2_32(uint32_t x) {
    /* __builtin_clz(x) повертає кількість провідних нулів у 32-бітному числі.
       Для коректності x має бути строго > 0. */
    return (size_t)(31 - __builtin_clz(x));
}

/* Макрос для знаходження мінімуму двох цілих чисел */
static inline int32_t st_min(int32_t a, int32_t b) {
    return (a < b) ? a : b;
}

/* Ініціалізація та виділення пам'яті для таблиці */
sparse_table_t *st_create(const int32_t *array, size_t n) {
    if (array == NULL || n == 0) {
        return NULL;
    }

    sparse_table_t *st = (sparse_table_t *)malloc(sizeof(sparse_table_t));
    if (st == NULL) {
        return NULL;
    }

    st->n = n;
    st->levels = st_log2_32((uint32_t)n) + 1;

    /* Виділяємо єдиний неперервний блок пам'яті для всіх рівнів */
    st->data = (int32_t *)malloc(st->levels * st->n * sizeof(int32_t));
    if (st->data == NULL) {
        free(st);
        return NULL;
    }

    /* Рівень j = 0: копіюємо вихідний масив */
    for (size_t i = 0; i < n; ++i) {
        st->data[0 * n + i] = array[i];
    }

    /* Рівні j >= 1: обчислюємо через динамічне програмування */
    for (size_t j = 1; j < st->levels; ++j) {
        size_t half = (size_t)1 << (j - 1);
        size_t row_curr = j * n;
        size_t row_prev = (j - 1) * n;

        for (size_t i = 0; i + ((size_t)1 << j) <= n; ++i) {
            st->data[row_curr + i] = st_min(st->data[row_prev + i],
                                            st->data[row_prev + i + half]);
        }
    }

    return st;
}

/* Константний запит Range Minimum Query O(1) для ідемпотентної операції */
bool st_query_min(const sparse_table_t *st, size_t l, size_t r, int32_t *result) {
    if (st == NULL || result == NULL || l > r || r >= st->n) {
        return false;
    }

    size_t len = r - l + 1;
    size_t k = st_log2_32((uint32_t)len);
    size_t shift = (size_t)1 << k;

    int32_t left_val = st->data[k * st->n + l];
    int32_t right_val = st->data[k * st->n + (r - shift + 1)];

    *result = st_min(left_val, right_val);
    return true;
}

/* Звільнення ресурсів */
void st_destroy(sparse_table_t *st) {
    if (st != NULL) {
        free(st->data);
        free(st);
    }
}
