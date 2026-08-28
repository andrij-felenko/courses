#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

// Система неперетинних множин (DSU) мовою C
typedef struct {
    int *parent;
    int *rank;
    int size;
} DSU;

DSU* dsu_create(int size) {
    DSU *dsu = (DSU*)malloc(sizeof(DSU));
    dsu->parent = (int*)malloc((size + 1) * sizeof(int));
    dsu->rank = (int*)calloc(size + 1, sizeof(int));
    dsu->size = size;
    for (int i = 0; i <= size; i++) {
        dsu->parent[i] = i;
    }
    return dsu;
}

void dsu_free(DSU *dsu) {
    free(dsu->parent);
    free(dsu->rank);
    free(dsu);
}

int dsu_find(DSU *dsu, int i) {
    if (dsu->parent[i] == i)
        return i;
    return dsu->parent[i] = dsu_find(dsu, dsu->parent[i]);
}

void dsu_unite(DSU *dsu, int i, int j) {
    int root_i = dsu_find(dsu, i);
    int root_j = dsu_find(dsu, j);
    if (root_i != root_j) {
        if (dsu->rank[root_i] < dsu->rank[root_j]) {
            int tmp = root_i; root_i = root_j; root_j = tmp;
        }
        dsu->parent[root_j] = root_i;
        if (dsu->rank[root_i] == dsu->rank[root_j]) {
            dsu->rank[root_i]++;
        }
    }
}

typedef struct {
    bool has_spanning_cluster;
    int total_clusters;
    int max_cluster_size;
    double occupied_fraction;
} PercolationResultC;

PercolationResultC run_percolation_simulation_c(int N, double p, unsigned int seed) {
    srand(seed);
    uint8_t *grid = (uint8_t*)calloc(N * N, sizeof(uint8_t));
    int occupied_count = 0;

    for (int i = 0; i < N * N; i++) {
        if ((double)rand() / RAND_MAX < p) {
            grid[i] = 1;
            occupied_count++;
        }
    }

    int *labels = (int*)calloc(N * N, sizeof(int));
    DSU *dsu = dsu_create(N * N / 2 + 2);
    int next_label = 1;

    for (int r = 0; r < N; r++) {
        for (int c = 0; c < N; c++) {
            int idx = r * N + c;
            if (!grid[idx]) continue;

            int left = (c > 0 && grid[idx - 1]) ? labels[idx - 1] : 0;
            int top = (r > 0 && grid[idx - N]) ? labels[idx - N] : 0;

            if (left == 0 && top == 0) {
                labels[idx] = next_label++;
            } else if (left != 0 && top == 0) {
                labels[idx] = left;
            } else if (left == 0 && top != 0) {
                labels[idx] = top;
            } else {
                labels[idx] = left;
                dsu_unite(dsu, left, top);
            }
        }
    }

    int *cluster_sizes = (int*)calloc(next_label, sizeof(int));
    for (int i = 0; i < N * N; i++) {
        if (labels[i] > 0) {
            labels[i] = dsu_find(dsu, labels[i]);
            cluster_sizes[labels[i]]++;
        }
    }

    uint8_t *top_roots = (uint8_t*)calloc(next_label, sizeof(uint8_t));
    uint8_t *bottom_roots = (uint8_t*)calloc(next_label, sizeof(uint8_t));

    for (int c = 0; c < N; c++) {
        if (labels[c] > 0) top_roots[labels[c]] = 1;
        if (labels[(N - 1) * N + c] > 0) bottom_roots[labels[(N - 1) * N + c]] = 1;
    }

    bool spanning = false;
    int active_clusters = 0;
    int max_size = 0;

    for (int l = 1; l < next_label; l++) {
        if (cluster_sizes[l] > 0 && dsu_find(dsu, l) == l) {
            active_clusters++;
            if (cluster_sizes[l] > max_size) {
                max_size = cluster_sizes[l];
            }
            if (top_roots[l] && bottom_roots[l]) {
                spanning = true;
            }
        }
    }

    PercolationResultC res = {
        spanning,
        active_clusters,
        max_size,
        (double)occupied_count / (N * N)
    };

    free(grid);
    free(labels);
    free(cluster_sizes);
    free(top_roots);
    free(bottom_roots);
    dsu_free(dsu);

    return res;
}

int main() {
    int N = 200;
    double p = 0.59274;
    PercolationResultC res = run_percolation_simulation_c(N, p, 12345);

    printf("Модель C — Ґратка %dx%d\n", N, N);
    printf("Частка відкритих вузлів: %.5f\n", res.occupied_fraction);
    printf("Протікання: %s\n", res.has_spanning_cluster ? "ТАК" : "НІ");
    printf("Кількість кластерів: %d\n", res.total_clusters);
    printf("Найбільший кластер: %d вузлів\n", res.max_cluster_size);

    return 0;
}
