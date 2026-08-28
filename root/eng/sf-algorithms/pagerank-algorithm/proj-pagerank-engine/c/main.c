#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

// Структура розрідженого графа у форматі CSR
typedef struct {
    int num_nodes;
    int num_edges;
    int* row_ptr;     // розмір num_nodes + 1
    int* col_idx;     // розмір num_edges
    int* out_degree;  // розмір num_nodes
} CsrGraph;

// Результат обчислення
typedef struct {
    double* ranks;
    int iterations;
    double final_diff;
    bool converged;
} PageRankResult;

// Створення графа
CsrGraph* create_graph(int num_nodes, int num_edges) {
    if (num_nodes <= 0 || num_edges < 0) return NULL;
    CsrGraph* g = (CsrGraph*)malloc(sizeof(CsrGraph));
    if (!g) return NULL;
    g->num_nodes = num_nodes;
    g->num_edges = num_edges;
    g->row_ptr = (int*)calloc(num_nodes + 1, sizeof(int));
    g->col_idx = (num_edges > 0) ? (int*)malloc(num_edges * sizeof(int)) : NULL;
    g->out_degree = (int*)calloc(num_nodes, sizeof(int));
    if (!g->row_ptr || (!g->col_idx && num_edges > 0) || !g->out_degree) {
        free(g->row_ptr);
        free(g->col_idx);
        free(g->out_degree);
        free(g);
        return NULL;
    }
    return g;
}

// Звільнення пам'яті графа
void free_graph(CsrGraph* g) {
    if (!g) return;
    free(g->row_ptr);
    free(g->col_idx);
    free(g->out_degree);
    free(g);
}

// Обчислення PageRank
PageRankResult compute_pagerank(const CsrGraph* g, double damping, double tol, int max_iter) {
    PageRankResult res = {NULL, 0, 0.0, false};
    int N = g ? g->num_nodes : 0;
    if (N <= 0) return res;

    double* r_cur = (double*)malloc(N * sizeof(double));
    double* r_next = (double*)malloc(N * sizeof(double));
    if (!r_cur || !r_next) {
        free(r_cur);
        free(r_next);
        return res;
    }

    // Ініціалізація рівномірним розподілом 1 / N
    double init_val = 1.0 / (double)N;
    for (int i = 0; i < N; ++i) {
        r_cur[i] = init_val;
    }

    int iter = 0;
    double diff = 0.0;

    while (iter < max_iter) {
        iter++;

        // 1. Акумуляція рангу висячих вузлів (out_degree == 0)
        double dangling_sum = 0.0;
        for (int u = 0; u < N; ++u) {
            if (g->out_degree[u] == 0) {
                dangling_sum += r_cur[u];
            }
        }

        // 2. Базовий рівномірний внесок телепортації для кожної вершини
        double base_rank = (damping * dangling_sum + (1.0 - damping)) / (double)N;
        for (int i = 0; i < N; ++i) {
            r_next[i] = base_rank;
        }

        // 3. Розподіл рангу вздовж орієнтованих ребер u -> v
        for (int u = 0; u < N; ++u) {
            int deg = g->out_degree[u];
            if (deg > 0) {
                double share = (damping * r_cur[u]) / (double)deg;
                int start = g->row_ptr[u];
                int end = g->row_ptr[u + 1];
                for (int e = start; e < end; ++e) {
                    int v = g->col_idx[e];
                    r_next[v] += share;
                }
            }
        }

        // 4. Оцінка похибки за L1-нормою: sum |r_next[i] - r_cur[i]|
        diff = 0.0;
        for (int i = 0; i < N; ++i) {
            diff += fabs(r_next[i] - r_cur[i]);
            r_cur[i] = r_next[i]; // копіюємо для наступного кроку
        }

        if (diff < tol) {
            res.converged = true;
            break;
        }
    }

    free(r_next);
    res.ranks = r_cur;
    res.iterations = iter;
    res.final_diff = diff;
    return res;
}
