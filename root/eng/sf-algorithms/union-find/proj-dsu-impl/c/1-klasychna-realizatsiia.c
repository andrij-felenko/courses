#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

typedef struct {
    int *parent;
    int *rank;
    size_t capacity;
    size_t num_sets;
} DSU;

DSU *dsu_create(size_t n) {
    DSU *dsu = (DSU *)malloc(sizeof(DSU));
    if (!dsu) return NULL;

    dsu->parent = (int *)malloc(n * sizeof(int));
    dsu->rank = (int *)calloc(n, sizeof(int));
    if (!dsu->parent || !dsu->rank) {
        free(dsu->parent);
        free(dsu->rank);
        free(dsu);
        return NULL;
    }

    dsu->capacity = n;
    dsu->num_sets = n;
    for (size_t i = 0; i < n; i++) {
        dsu->parent[i] = (int)i;
    }
    return dsu;
}

void dsu_destroy(DSU *dsu) {
    if (!dsu) return;
    free(dsu->parent);
    free(dsu->rank);
    free(dsu);
}

int dsu_find(DSU *dsu, int x) {
    if (x < 0 || (size_t)x >= dsu->capacity) return -1;
    
    // Рекурсивне стиснення шляху (Path Compression)
    if (dsu->parent[x] != x) {
        dsu->parent[x] = dsu_find(dsu, dsu->parent[x]);
    }
    return dsu->parent[x];
}

bool dsu_union(DSU *dsu, int x, int y) {
    int root_x = dsu_find(dsu, x);
    int root_y = dsu_find(dsu, y);

    if (root_x == -1 || root_y == -1 || root_x == root_y) {
        return false;
    }

    // Об'єднання за рангом (Union by Rank)
    if (dsu->rank[root_x] < dsu->rank[root_y]) {
        dsu->parent[root_x] = root_y;
    } else if (dsu->rank[root_x] > dsu->rank[root_y]) {
        dsu->parent[root_y] = root_x;
    } else {
        dsu->parent[root_y] = root_x;
        dsu->rank[root_x]++;
    }

    dsu->num_sets--;
    return true;
}
