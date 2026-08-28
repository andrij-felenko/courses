#include <stdio.h>
#include <stddef.h>

/* Функція вищого порядку: фільтрує масив за предикатом з контекстом */
typedef int (*predicate_fn)(int value, void *ctx);

size_t filter_integers(const int *src, size_t len, int *dst,
                       predicate_fn pred, void *ctx) {
    size_t out_count = 0;
    for (size_t i = 0; i < len; ++i) {
        if (pred(src[i], ctx)) {
            dst[out_count++] = src[i];
        }
    }
    return out_count;
}

/* Конкретний предикат: перевірка на перевищення порогу */
static int is_greater_than(int val, void *ctx) {
    int threshold = *(int *)ctx;
    return val > threshold;
}

int main(void) {
    int data[] = {12, 45, 3, 89, 23, 67, 8};
    int results[7];
    int threshold = 25;

    size_t count = filter_integers(data, 7, results, is_greater_than, &threshold);

    for (size_t i = 0; i < count; ++i) {
        printf("%d ", results[i]); /* 45 89 67 */
    }
    printf("\n");
    return 0;
}
