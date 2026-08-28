#include <stddef.h>

/* Структура з великим навантаженням даних */
typedef struct {
    int id;
    double score;
    char payload[1024]; /* 1 КБ корисного навантаження */
} HeavyRecord;

/* Непряме сортування масиву покажчиків на важкі структури */
void indirect_insertion_sort(HeavyRecord **ptrs, size_t n) {
    if (ptrs == NULL || n <= 1) {
        return;
    }

    for (size_t i = 1; i < n; ++i) {
        HeavyRecord *key = ptrs[i];
        size_t j = i;

        /* Порівнюємо значення через покажчики, але переставляємо лише самі адреси */
        while (j > 0 && ptrs[j - 1]->score > key->score) {
            ptrs[j] = ptrs[j - 1];
            --j;
        }
        ptrs[j] = key;
    }
}
