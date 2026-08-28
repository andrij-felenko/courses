#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

#define MIN_VAL(a, b) (((a) < (b)) ? (a) : (b))

/* Ітеративне злиття двох сусідніх блоків розміром width із src у dst */
static void merge_blocks(const int *src, int *dst, size_t lo, size_t mid, size_t hi) {
    size_t i = lo;
    size_t j = mid;
    size_t k = lo;

    while (i < mid && j < hi) {
        if (src[i] <= src[j]) {
            dst[k++] = src[i++];
        } else {
            dst[k++] = src[j++];
        }
    }

    while (i < mid) {
        dst[k++] = src[i++];
    }
    while (j < hi) {
        dst[k++] = src[j++];
    }
}

/* Висхідне ітеративне сортування злиттям з подвійним буфером */
bool merge_sort_bottom_up(int *arr, size_t n) {
    if (!arr || n <= 1) {
        return true;
    }

    int *aux = (int *)malloc(n * sizeof(int));
    if (!aux) {
        return false;
    }

    int *src = arr;
    int *dst = aux;

    /* Подвоєння ширини блоків: 1, 2, 4, 8, 16 ... */
    for (size_t width = 1; width < n; width *= 2) {
        for (size_t i = 0; i < n; i += 2 * width) {
            size_t lo = i;
            size_t mid = MIN_VAL(i + width, n);
            size_t hi = MIN_VAL(i + 2 * width, n);
            merge_blocks(src, dst, lo, mid, hi);
        }

        /* Зміна ролей буферів (Ping-Pong перемикання) */
        int *temp = src;
        src = dst;
        dst = temp;
    }

    /* Якщо фінальний результат опинився в aux, копіюємо його назад в arr */
    if (src != arr) {
        for (size_t i = 0; i < n; ++i) {
            arr[i] = src[i];
        }
    }

    free(aux);
    return true;
}
