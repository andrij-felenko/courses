#include <stdlib.h>

// 1. Виділення пам'яті
size_t n = 100;
int *arr = (int *)malloc(n * sizeof(int));
if (!arr) {
    // Обробка помилки браку пам'яті
}

// 2. Ініціалізація нулями (альтернатива через calloc)
int *zero_arr = (int *)calloc(n, sizeof(int));

// 3. Динамічна зміна розміру
size_t new_n = 200;
int *temp = (int *)realloc(arr, new_n * sizeof(int));
if (temp) {
    arr = temp;
} else {
    // У разі помилки старий блок arr залишається дійсним!
}

// 4. Обов'язкове звільнення пам'яті
free(arr);
arr = NULL;
