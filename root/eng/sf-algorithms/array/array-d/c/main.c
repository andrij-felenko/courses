#include <stdio.h>
#include <stdlib.h>

int main(void) {
    // 1. Статичний масив на стеку
    int static_arr[5] = {10, 20, 30, 40, 50};
    printf("Статичний масив A[2] = %d\n", static_arr[2]);

    // 2. Динамічний масив у купі (Heap)
    size_t capacity = 4;
    size_t size = 0;
    int *dyn_arr = (int *)malloc(capacity * sizeof(int));
    if (!dyn_arr) return 1;

    // Додавання елементів з динамічним розширенням x2
    for (int i = 0; i < 10; ++i) {
        if (size == capacity) {
            capacity *= 2;
            int *temp = (int *)realloc(dyn_arr, capacity * sizeof(int));
            if (!temp) {
                free(dyn_arr);
                return 1;
            }
            dyn_arr = temp;
        }
        dyn_arr[size++] = (i + 1) * 100;
    }

    printf("Динамічний масив: розмір = %zu, місткість = %zu\n", size, capacity);
    printf("Елемент [5] = %d\n", dyn_arr[5]);

    free(dyn_arr);
    return 0;
}
