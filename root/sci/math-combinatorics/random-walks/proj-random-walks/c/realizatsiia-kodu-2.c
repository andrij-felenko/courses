#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

typedef struct {
    int num_vertices;
    int** out_adj;
    int* out_degrees;
} DigraphC;

DigraphC* digraph_create(int n) {
    DigraphC* g = (DigraphC*)malloc(sizeof(DigraphC));
    g->num_vertices = n;
    g->out_degrees = (int*)calloc(n, sizeof(int));
    g->out_adj = (int**)malloc(n * sizeof(int*));
    for (int i = 0; i < n; i++) g->out_adj[i] = NULL;
    return g;
}

void digraph_add_edge(DigraphC* g, int u, int v) {
    g->out_degrees[u]++;
    g->out_adj[u] = (int*)realloc(g->out_adj[u], g->out_degrees[u] * sizeof(int));
    g->out_adj[u][g->out_degrees[u] - 1] = v;
}

void digraph_free(DigraphC* g) {
    for (int i = 0; i < g->num_vertices; i++) free(g->out_adj[i]);
    free(g->out_adj);
    free(g->out_degrees);
    free(g);
}

// Обчислення PageRank методом Монте-Карло
void compute_pagerank_monte_carlo(const DigraphC* g, double alpha, int num_walks, int walk_length, double* rank_out) {
    int n = g->num_vertices;
    long long* visit_counts = (long long*)calloc(n, sizeof(long long));
    long long total_visits = 0;

    for (int w = 0; w < num_walks; w++) {
        int curr = rand() % n;
        visit_counts[curr]++;
        total_visits++;

        for (int step = 0; step < walk_length; step++) {
            double r = (double)rand() / RAND_MAX;
            int out_deg = g->out_degrees[curr];

            if (r < alpha && out_deg > 0) {
                // Перехід по сужному ребру
                int next_idx = rand() % out_deg;
                curr = g->out_adj[curr][next_idx];
            } else {
                // Телепортація
                curr = rand() % n;
            }
            visit_counts[curr]++;
            total_visits++;
        }
    }

    for (int i = 0; i < n; i++) {
        rank_out[i] = (double)visit_counts[i] / total_visits;
    }
    free(visit_counts);
}
