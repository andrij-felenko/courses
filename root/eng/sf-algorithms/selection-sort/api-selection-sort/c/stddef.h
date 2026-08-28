#include <stddef.h>

/*
 * Сортування масиву цілих чисел типу int.
 *
 * @param arr Покажчик на перший елемент масиву. Повинен бути не-NULL.
 * @param n   Кількість елементів у масиві.
 */
void selection_sort_int(int *arr, size_t n);

/*
 * Універсальне сортування буфера довільного типу за аналогією з qsort().
 *
 * @param base Покажчик на початок буфера пам'яті.
 * @param num  Кількість елементів у буфері.
 * @param size Розмір одного елемента в байтах (sizeof(T)).
 * @param cmp  Функція-компаратор: повертає <0 якщо (a < b), 0 якщо (a == b), >0 якщо (a > b).
 */
void selection_sort_generic(void *base, size_t num, size_t size,
                            int (*cmp)(const void *a, const void *b));

/*
 * Двостороннє сортування вибором (Min-Max Selection Sort).
 * Зменшує кількість ітерацій зовнішнього циклу у 2 рази.
 */
void double_selection_sort(int *arr, size_t n);

/*
 * Стійке сортування вибором (Stable Selection Sort).
 * Застосовує зсув елементів замість прямого swap, зберігаючи відносний порядок.
 */
void stable_selection_sort(int *arr, size_t n);
