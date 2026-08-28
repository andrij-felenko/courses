#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

#define MAX_VERTICES 64

typedef struct {
    int num_vertices;
    uint64_t adj[MAX_VERTICES]; /* adj[i] бітова маска: j-й біт = 1 (червоне), 0 (синє) */
} ramsey_graph_t;

static void graph_init(ramsey_graph_t *g, int n) {
    g->num_vertices = n;
    for (int i = 0; i < n; i++) {
        g->adj[i] = 0;
    }
}

static void graph_set_edge(ramsey_graph_t *g, int u, int v, bool is_red) {
    if (is_red) {
        g->adj[u] |= (1ULL << v);
        g->adj[v] |= (1ULL << u);
    } else {
        g->adj[u] &= ~(1ULL << v);
        g->adj[v] &= ~(1ULL << u);
    }
}

/* Рекурсивна перевірка існування монохроматичної кліки target_size */
static bool check_clique_rec(const ramsey_graph_t *g, uint64_t candidates, int target_size, int current_size, bool is_red) {
    if (current_size == target_size) {
        return true;
    }

    while (candidates > 0) {
        /* Враховуємо кількість залишку для прискорення (pruning) */
        int popcount = __builtin_popcountll(candidates);
        if (current_size + popcount < target_size) {
            return false;
        }

        int v = __builtin_ctzll(candidates);
        candidates &= ~(1ULL << v);

        uint64_t neighbors = is_red ? g->adj[v] : ~(g->adj[v]);
        /* Виключаємо вершини зі старшими індексами для унікальності порядку */
        uint64_t mask_future = ~((1ULL << (v + 1)) - 1);
        uint64_t next_candidates = candidates & neighbors & mask_future;

        if (check_clique_rec(g, next_candidates, target_size, current_size + 1, is_red)) {
            return true;
        }
    }
    return false;
}

/* Визначення, чи містить граф червоний K_r чи синій K_s */
bool ramsey_has_monochromatic_clique(const ramsey_graph_t *g, int r, int s) {
    uint64_t all_vertices = (g->num_vertices == 64) ? ~0ULL : ((1ULL << g->num_vertices) - 1);

    /* Перевіряємо червоний K_r */
    if (check_clique_rec(g, all_vertices, r, 0, true)) {
        return true;
    }

    /* Перевіряємо синій K_s */
    if (check_clique_rec(g, all_vertices, s, 0, false)) {
        return true;
    }

    return false;
}

/* Пошук контрприкладу розфарбування методом рекурсивного пошуку з поверненням */
static bool search_counterexample_rec(ramsey_graph_t *g, int edge_idx, int total_edges, int edge_u[], int edge_v[], int r, int s) {
    if (edge_idx == total_edges) {
        return !ramsey_has_monochromatic_clique(g, r, s);
    }

    int u = edge_u[edge_idx];
    int v = edge_v[edge_idx];

    /* Спробувати червоне ребро */
    graph_set_edge(g, u, v, true);
    if (search_counterexample_rec(g, edge_idx + 1, total_edges, edge_u, edge_v, r, s)) {
        return true;
    }

    /* Спробувати синє ребро */
    graph_set_edge(g, u, v, false);
    if (search_counterexample_rec(g, edge_idx + 1, total_edges, edge_u, edge_v, r, s)) {
        return true;
    }

    return false;
}

bool ramsey_find_counterexample(ramsey_graph_t *out_graph, int n, int r, int s) {
    graph_init(out_graph, n);
    int total_edges = n * (n - 1) / 2;
    int *edge_u = (int *)malloc(total_edges * sizeof(int));
    int *edge_v = (int *)malloc(total_edges * sizeof(int));

    if (!edge_u || !edge_v) {
        free(edge_u);
        free(edge_v);
        return false;
    }

    int idx = 0;
    for (int i = 0; i < n; i++) {
        for (int j = i + 1; j < n; j++) {
            edge_u[idx] = i;
            edge_v[idx] = j;
            idx++;
        }
    }

    bool found = search_counterexample_rec(out_graph, 0, total_edges, edge_u, edge_v, r, s);

    free(edge_u);
    free(edge_v);
    return found;
}

int main(void) {
    printf("=== Перевірка чисел Рамсея (C Implementation) ===\n");
    int r = 3, s = 3;

    for (int n = 3; n <= 6; n++) {
        ramsey_graph_t g;
        bool has_counterexample = ramsey_find_counterexample(&g, n, r, s);
        if (has_counterexample) {
            printf("n = %d: Знайдено контрприклад! R(%d, %d) > %d\n", n, r, s, n);
        } else {
            printf("n = %d: Не існує контрприкладу. Отже R(%d, %d) <= %d\n", n, r, s, n);
        }
    }

    return 0;
}
