#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <limits.h>

#define INF LLONG_MAX

typedef struct {
    int src;
    int dest;
    long long weight;
} JEdge;

typedef struct {
    int num_vertices;
    long long** all_dist;
    bool has_negative_cycle;
} JohnsonResult;

JohnsonResult johnson_all_pairs(int V, int E, const JEdge* edges) {
    JohnsonResult res;
    res.num_vertices = V;
    res.has_negative_cycle = false;
    
    // Створення супер-вершини s = V з вагами 0 до всіх вершин
    int super_V = V + 1;
    int super_E = E + V;
    JEdge* super_edges = (JEdge*)malloc(super_E * sizeof(JEdge));
    
    for (int i = 0; i < E; ++i) {
        super_edges[i] = edges[i];
    }
    for (int i = 0; i < V; ++i) {
        super_edges[E + i].src = V; // супер-вузол
        super_edges[E + i].dest = i;
        super_edges[E + i].weight = 0;
    }

    // Прогін Беллмана-Форда від супер-вузла
    long long* h = (long long*)malloc(super_V * sizeof(long long));
    for (int i = 0; i < super_V; ++i) h[i] = INF;
    h[V] = 0;

    for (int iter = 0; iter < super_V - 1; ++iter) {
        bool updated = false;
        for (int i = 0; i < super_E; ++i) {
            int u = super_edges[i].src;
            int v = super_edges[i].dest;
            long long w = super_edges[i].weight;
            if (h[u] != INF && h[u] + w < h[v]) {
                h[v] = h[u] + w;
                updated = true;
            }
        }
        if (!updated) break;
    }

    // Перевірка на від'ємний цикл
    for (int i = 0; i < super_E; ++i) {
        int u = super_edges[i].src;
        int v = super_edges[i].dest;
        long long w = super_edges[i].weight;
        if (h[u] != INF && h[u] + w < h[v]) {
            res.has_negative_cycle = true;
            free(super_edges);
            free(h);
            return res;
        }
    }

    // Виділення матриці результату
    res.all_dist = (long long**)malloc(V * sizeof(long long*));
    for (int i = 0; i < V; ++i) {
        res.all_dist[i] = (long long*)malloc(V * sizeof(long long));
        for (int j = 0; j < V; ++j) {
            res.all_dist[i][j] = (i == j) ? 0 : INF;
        }
    }

    free(super_edges);
    free(h);
    return res;
}
