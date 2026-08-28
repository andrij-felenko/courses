#include <stdio.h>
#include <stddef.h>

// Класичний пошук: 2 розгалуження на кожну ітерацію циклу
size_t linear_search_classic(const int* arr, size_t n, int target) {
    for (size_t i = 0; i < n; ++i) {
        if (arr[i] == target) {
            return i;
        }
    }
    return (size_t)-1;
}

// Пошук із вартовим: рівно 1 розгалуження в тілі циклу!
// Масив arr повинен мати виділений розмір щонайменше (n + 1).
size_t linear_search_sentinel(int* arr, size_t n, int target) {
    arr[n] = target; // Ставимо вартового на кінець масиву
    size_t i = 0;
    while (arr[i] != target) {
        i++;
    }
    // Якщо зупинилися до n — елемент справжній, якщо на n — спрацював вартовий
    return (i < n) ? i : (size_t)-1;
}
