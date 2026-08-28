#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

// Перевіряє, чи є підмножина mask монохроматичною та великою (|H| >= min(H) та |H| >= m)
static bool check_monochromatic_large(const int *coloring, int n_nodes, int mask, int m, int *out_color) {
    int count = 0;
    int min_val = n_nodes + 1;

    for (int i = 0; i < n_nodes; ++i) {
        if ((mask >> i) & 1) {
            count++;
            int val = i + 1; // Нумерація вершин від 1
            if (val < min_val) {
                min_val = val;
            }
        }
    }

    // Перевірка умов розміру та великої множини
    if (count < m || count < min_val) {
        return false;
    }

    // Перевірка однорідності кольору всіх ребер усередині підмножини
    int target_color = -1;
    for (int i = 0; i < n_nodes; ++i) {
        if (!((mask >> i) & 1)) continue;
        for (int j = i + 1; j < n_nodes; ++j) {
            if (!((mask >> j) & 1)) continue;

            int edge_idx = i * n_nodes + j;
            int c = coloring[edge_idx];
            if (target_color == -1) {
                target_color = c;
            } else if (target_color != c) {
                return false; // Знайдено ребро іншого кольору
            }
        }
    }

    if (out_color) *out_color = target_color;
    return true;
}

// Шукає, чи містить дане розфарбування графів K_N хоча б одну велику монохроматичну підмножину
static bool has_large_monochromatic_set(const int *coloring, int n_nodes, int m) {
    int total_subsets = 1 << n_nodes;
    for (int mask = 1; mask < total_subsets; ++mask) {
        if (check_monochromatic_large(coloring, n_nodes, mask, m, NULL)) {
            return true;
        }
    }
    return false;
}

// Пошук розфарбування без великих монохроматичних підмножин методом рекурсивного перебору
static bool find_bad_coloring(int *coloring, int n_nodes, int u, int v, int m) {
    if (u >= n_nodes - 1) {
        // Усі ребра розфарбовано, перевіряємо наявність великої монохроматичної підмножини
        return !has_large_monochromatic_set(coloring, n_nodes, m);
    }

    int next_u = u;
    int next_v = v + 1;
    if (next_v >= n_nodes) {
        next_u = u + 1;
        next_v = next_u + 1;
    }

    // Пробуємо колір 0
    coloring[u * n_nodes + v] = 0;
    coloring[v * n_nodes + u] = 0;
    if (find_bad_coloring(coloring, n_nodes, next_u, next_v, m)) {
        return true;
    }

    // Пробуємо колір 1
    coloring[u * n_nodes + v] = 1;
    coloring[v * n_nodes + u] = 1;
    if (find_bad_coloring(coloring, n_nodes, next_u, next_v, m)) {
        return true;
    }

    return false;
}

int main(void) {
    printf("Обчислення малих чисел Паріса — Гаррінгтона PH(2, m, 2):\n");
    int m = 3;

    for (int N = m; N <= 20; ++N) {
        int *coloring = (int *)calloc(N * N, sizeof(int));
        if (!coloring) {
            fprintf(stderr, "Помилка виділення пам'яті\n");
            return 1;
        }

        bool bad_found = find_bad_coloring(coloring, N, 0, 1, m);
        free(coloring);

        if (!bad_found) {
            printf("Знайдено мінімальний поріг PH(2, %d, 2) = %d\n", m, N);
            break;
        } else {
            printf("N = %2d: існує розфарбування без великих монохроматичних множин\n", N);
        }
    }

    return 0;
}
