#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

#define INF 1e9

typedef struct {
    double min_cost;
    int* path;
    size_t path_len;
} tsp_solution_t;

/**
 * Точний розв'язок задачі комівояжера алгоритмом Хелда-Карпа на мові C.
 * Приймає плоску матрицю відстаней розміром n x n у форматі row-major.
 */
tsp_solution_t tsp_held_karp_c(const double* matrix, size_t n) {
    tsp_solution_t res = {INF, NULL, 0};
    
    /* Перевірка граничних умов: бітові маски uint32_t обмежені 32 вершинами,
       але практичний ліміт пам'яті досягається при n <= 20 (2^20 * 20 * 8 байт ≈ 168 МБ) */
    if (n == 0 || n > 20) {
        return res;
    }

    size_t num_states = 1U << n;
    
    /* Виділення суцільного блоку пам'яті для DP-таблиці та баз даних відновлення шляху */
    double* dp = (double*)malloc(num_states * n * sizeof(double));
    int* parent = (int*)malloc(num_states * n * sizeof(int));

    if (!dp || !parent) {
        free(dp);
        free(parent);
        return res;
    }

    /* Ініціалізація DP-таблиці нескінченністю INF */
    for (size_t s = 0; s < num_states; ++s) {
        for (size_t i = 0; i < n; ++i) {
            dp[s * n + i] = INF;
            parent[s * n + i] = -1;
        }
    }

    /* Базовий стан: старт у вершині 0, у масці встановлено лише 0-й біт (1U << 0) */
    dp[(1U << 0) * n + 0] = 0.0;

    /* Ітерація за зростанням бітової маски запевнює, що підзадачі меншого розміру
       обчислюються раніше за підзадачі більшого розміру */
    for (uint32_t mask = 1; mask < num_states; ++mask) {
        /* Якщо 0-й біт не встановлено, дана маска не містить початкову вершину 0 */
        if (!(mask & 1U)) continue;

        for (size_t u = 0; u < n; ++u) {
            /* Перевіряємо, чи входить вершина u до поточної маски */
            if (!(mask & (1U << u))) continue;
            
            double current_cost = dp[mask * n + u];
            if (current_cost >= INF) continue;

            /* Пробуємо перейти до всіх ще не відвіданих вершин v */
            for (size_t v = 0; v < n; ++v) {
                if (mask & (1U << v)) continue; /* Вершина v вже відвідана */

                uint32_t next_mask = mask | (1U << v);
                double weight = matrix[u * n + v];
                double new_cost = current_cost + weight;

                /* Оновлюємо рекурентне співвідношення Хелда-Карпа */
                if (new_cost < dp[next_mask * n + v]) {
                    dp[next_mask * n + v] = new_cost;
                    parent[next_mask * n + v] = (int)u;
                }
            }
        }
    }

    /* Фінальний крок: знаходження найкращого замикання циклу назад до вершини 0 */
    uint32_t full_mask = (1U << n) - 1;
    size_t last_node = 0;
    
    for (size_t u = 1; u < n; ++u) {
        double cost = dp[full_mask * n + u] + matrix[u * n + 0];
        if (cost < res.min_cost) {
            res.min_cost = cost;
            last_node = u;
        }
    }

    /* Відновлення послідовності вершин шляхом зворотного проходу по масиву parent */
    res.path = (int*)malloc((n + 1) * sizeof(int));
    if (res.path) {
        res.path_len = n + 1;
        uint32_t curr_mask = full_mask;
        size_t curr_node = last_node;
        
        for (int i = (int)n - 1; i >= 1; --i) {
            res.path[i] = (int)curr_node;
            int prev = parent[curr_mask * n + curr_node];
            curr_mask ^= (1U << curr_node);
            curr_node = (size_t)prev;
        }
        res.path[0] = 0;
        res.path[n] = 0;
    }

    free(dp);
    free(parent);
    return res;
}
