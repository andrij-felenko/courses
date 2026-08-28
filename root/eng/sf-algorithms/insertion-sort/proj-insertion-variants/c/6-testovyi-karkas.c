#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <assert.h>

typedef struct {
    int key;
    int original_index;
} StableItem;

/* Сортування масиву структур для тестування стабільності */
void insertion_sort_stable(StableItem *arr, size_t n) {
    for (size_t i = 1; i < n; ++i) {
        StableItem item = arr[i];
        size_t j = i;
        /* Строга умова arr[j-1].key > item.key гарантує стійкість */
        while (j > 0 && arr[j - 1].key > item.key) {
            arr[j] = arr[j - 1];
            --j;
        }
        arr[j] = item;
    }
}

/* Перевірка відсортованості та стійкості порядку однакових ключів */
bool verify_sorted_and_stable(const StableItem *arr, size_t n) {
    for (size_t i = 1; i < n; ++i) {
        if (arr[i].key < arr[i - 1].key) {
            return false; /* Порушено порядок ключів */
        }
        if (arr[i].key == arr[i - 1].key && arr[i].original_index < arr[i - 1].original_index) {
            return false; /* Порушено взаємний порядок однакових елементів */
        }
    }
    return true;
}

void run_test_suite(void) {
    const size_t test_size = 100;
    StableItem *items = (StableItem*)malloc(test_size * sizeof(StableItem));
    assert(items != NULL);

    /* Заповнюємо масив з багатьма дублікатами ключів */
    for (size_t i = 0; i < test_size; ++i) {
        items[i].key = (int)(i % 7); /* Ключі від 0 до 6 */
        items[i].original_index = (int)i;
    }

    insertion_sort_stable(items, test_size);
    assert(verify_sorted_and_stable(items, test_size));

    free(items);
}
