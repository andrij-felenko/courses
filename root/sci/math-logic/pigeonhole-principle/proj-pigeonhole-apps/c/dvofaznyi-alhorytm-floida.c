#include <stdio.h>

int find_duplicate_floyd(const int* arr, size_t size) {
    if (size <= 1 || arr == NULL) return -1;

    // Фаза 1: Пошук точки зустрічі всередині циклу
    int slow = arr[0];
    int fast = arr[arr[0]];

    while (slow != fast) {
        slow = arr[slow];
        fast = arr[arr[fast]];
    }

    // Фаза 2: Пошук точки входу в цикл (колізії Діріхле)
    fast = 0;
    while (slow != fast) {
        slow = arr[slow];
        fast = arr[fast];
    }

    return slow;
}

int main(void) {
    // Масив розміром N + 1 = 6 елементів (значення від 1 до 5)
    int numbers[] = { 3, 1, 3, 4, 2, 5 };
    size_t size = sizeof(numbers) / sizeof(numbers[0]);

    int dup = find_duplicate_floyd(numbers, size);
    printf("Масив з %zu елементів (значення 1..%zu): елемент-дублікат = %d\n",
           size, size - 1, dup);

    return 0;
}
