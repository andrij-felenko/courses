#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

/**
 * Обчислення повної довжини замкненого маршруту за матрицею відстаней.
 */
static double calculate_tour_length(const int* tour, size_t n, const double* matrix) {
    double len = 0.0;
    for (size_t i = 0; i < n; ++i) {
        size_t u = (size_t)tour[i];
        size_t v = (size_t)tour[(i + 1) % n];
        len += matrix[u * n + v];
    }
    return len;
}

/**
 * Локальна оптимізація маршруту алгоритмом 2-Opt у стилі C.
 * Виконує ітеративний розворот підмасивів до досягнення локального оптимуму.
 */
void tsp_2opt_refine_c(int* tour, size_t n, const double* matrix) {
    if (n < 4) return;
    bool improved = true;

    while (improved) {
        improved = false;
        for (size_t i = 0; i < n - 1; ++i) {
            for (size_t j = i + 2; j < n; ++j) {
                /* Пропускаємо випадок, коли i=0 та j=n-1, оскільки це та сама пара ребер */
                if (i == 0 && j == n - 1) continue;

                size_t u = (size_t)tour[i];
                size_t v = (size_t)tour[i + 1];
                size_t x = (size_t)tour[j];
                size_t y = (size_t)tour[(j + 1) % n];

                double current_dist = matrix[u * n + v] + matrix[x * n + y];
                double new_dist = matrix[u * n + x] + matrix[v * n + y];

                /* Враховуємо похибку плаваючої крапки 1e-9 для уникнення нескінченних циклів */
                if (new_dist < current_dist - 1e-9) {
                    /* Реверс підмасиву елементів від i+1 до j включно */
                    size_t left = i + 1, right = j;
                    while (left < right) {
                        int temp = tour[left];
                        tour[left] = tour[right];
                        tour[right] = temp;
                        left++;
                        right--;
                    }
                    improved = true;
                }
            }
        }
    }
}
