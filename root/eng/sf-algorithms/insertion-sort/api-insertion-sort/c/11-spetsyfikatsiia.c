#include <stddef.h>

/**
 * @brief Сортує підмасив у межах більшого масиву [left, right] включно.
 * 
 * @param arr   Вказівник на початок базового масиву.
 * @param left  Індекс першого елемента підмасиву.
 * @param right Індекс останнього елемента підмасиву (включно).
 */
void insertion_sort_subrange(int *arr, size_t left, size_t right);
