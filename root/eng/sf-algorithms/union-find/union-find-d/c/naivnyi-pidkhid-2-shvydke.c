#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

// Реалізація Quick-Union без оптимізацій
typedef struct {
    int *parent;
    size_t size;
} QuickUnionDSU;

QuickUnionDSU *qu_create(size_t n) {
    QuickUnionDSU *dsu = (QuickUnionDSU *)malloc(sizeof(QuickUnionDSU));
    dsu->parent = (int *)malloc(n * sizeof(int));
    dsu->size = n;
    for (size_t i = 0; i < n; i++) {
        dsu->parent[i] = (int)i;
    }
    return dsu;
}

int qu_find(QuickUnionDSU *dsu, int x) {
    while (x != dsu->parent[x]) {
        x = dsu->parent[x];
    }
    return x;
}

void qu_union(QuickUnionDSU *dsu, int x, int y) {
    int root_x = qu_find(dsu, x);
    int root_y = qu_find(dsu, y);
    if (root_x != root_y) {
        dsu->parent[root_x] = root_y;
    }
}

void qu_destroy(QuickUnionDSU *dsu) {
    free(dsu->parent);
    free(dsu);
}
