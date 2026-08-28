#include <stddef.h>
#include <string.h>

/* Бінарний пошук верхньої межі (upper bound) для збереження стійкості */
static size_t binary_search_insertion_point(const int *arr, size_t len, int key) {
    size_t low = 0;
    size_t high = len;

    while (low < high) {
        size_t mid = low + (high - low) / 2;
        if (key < arr[mid]) {
            high = mid;
        } else {
            /* Якщо елементи рівні, зміщуємося праворуч (гарантія стабільності) */
            low = mid + 1;
        }
    }
    return low;
}

/* Двійкове сортування вставками з блоковим зсувом через memmove */
void binary_insertion_sort(int *arr, size_t n) {
    if (arr == NULL || n <= 1) {
        return;
    }

    for (size_t i = 1; i < n; ++i) {
        int key = arr[i];
        
        /* Знаходимо позицію за O(log i) порівнянь */
        size_t pos = binary_search_insertion_point(arr, i, key);

        /* Якщо ключ не на своєму місці, зсуваємо весь блок за одну операцію */
        if (pos < i) {
            memmove(&arr[pos + 1], &arr[pos], (i - pos) * sizeof(int));
            arr[pos] = key;
        }
    }
}
