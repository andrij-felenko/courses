/* Реалізація мовою C: оператор різниць та накопичувальне відновлення */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

typedef struct {
    int64_t* diff;
    size_t size;
} DifferenceArray1D;

bool diff_array_init(DifferenceArray1D* da, const int32_t* init_arr, size_t n) {
    if (!da || n == 0) return false;
    
    /* Додаємо 1 додатковий елемент для безпечного виконання diff[r + 1] -= val */
    da->diff = (int64_t*)calloc(n + 1, sizeof(int64_t));
    if (!da->diff) return false;
    
    da->size = n;
    if (init_arr) {
        da->diff[0] = init_arr[0];
        for (size_t i = 1; i < n; ++i) {
            da->diff[i] = (int64_t)init_arr[i] - (int64_t)init_arr[i - 1];
        }
    }
    return true;
}

/* Додавання значення val на відрізку [l, r] за O(1) */
void diff_array_add_range(DifferenceArray1D* da, size_t l, size_t r, int64_t val) {
    if (!da || !da->diff || l > r || r >= da->size) return;
    
    da->diff[l] += val;
    da->diff[r + 1] -= val;
}

/* Відновлення вихідного масиву префіксними сумами за O(N) */
bool diff_array_build(const DifferenceArray1D* da, int64_t* result_out, size_t out_size) {
    if (!da || !da->diff || !result_out || out_size < da->size) return false;
    
    int64_t current_sum = 0;
    for (size_t i = 0; i < da->size; ++i) {
        current_sum += da->diff[i];
        result_out[i] = current_sum;
    }
    return true;
}

void diff_array_free(DifferenceArray1D* da) {
    if (da && da->diff) {
        free(da->diff);
        da->diff = NULL;
        da->size = 0;
    }
}
