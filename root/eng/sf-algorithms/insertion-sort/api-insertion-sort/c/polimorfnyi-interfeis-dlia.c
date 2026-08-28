#include <stddef.h>

/**
 * @brief Сортує масив довільних об'єктів методом прямих вставок.
 * 
 * @param base   Вказівник на перший елемент масиву.
 * @param nel    Кількість елементів у масиві.
 * @param width  Розмір одного елемента в байтах (sizeof(T)).
 * @param compar Вказівник на функцію порівняння двох елементів.
 * 
 * @return void
 */
void insertion_sort_generic(
    void *base,
    size_t nel,
    size_t width,
    int (*compar)(const void *, const void *)
);
