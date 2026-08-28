#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

typedef struct {
    int root;
    int parity;
} FindResult;

typedef struct {
    int *parent;
    int *parity;
    size_t capacity;
} BipartiteDSU;

BipartiteDSU *bipartite_dsu_create(size_t n) {
    BipartiteDSU *dsu = (BipartiteDSU *)malloc(sizeof(BipartiteDSU));
    if (!dsu) return NULL;

    dsu->parent = (int *)malloc(n * sizeof(int));
    dsu->parity = (int *)calloc(n, sizeof(int));
    if (!dsu->parent || !dsu->parity) {
        free(dsu->parent);
        free(dsu->parity);
        free(dsu);
        return NULL;
    }

    dsu->capacity = n;
    for (size_t i = 0; i < n; i++) {
        dsu->parent[i] = (int)i;
    }
    return dsu;
}

void bipartite_dsu_destroy(BipartiteDSU *dsu) {
    if (!dsu) return;
    free(dsu->parent);
    free(dsu->parity);
    free(dsu);
}

FindResult bipartite_dsu_find(BipartiteDSU *dsu, int x) {
    if (dsu->parent[x] == x) {
        return (FindResult){.root = x, .parity = 0};
    }
    
    int p = dsu->parent[x];
    FindResult res = bipartite_dsu_find(dsu, p);
    
    // Оновлюємо покажчик батька та парність відносно кореня
    dsu->parent[x] = res.root;
    dsu->parity[x] ^= res.parity;
    
    return (FindResult){.root = dsu->parent[x], .parity = dsu->parity[x]};
}

bool bipartite_dsu_add_edge(BipartiteDSU *dsu, int x, int y) {
    FindResult rx = bipartite_dsu_find(dsu, x);
    FindResult ry = bipartite_dsu_find(dsu, y);

    if (rx.root == ry.root) {
        // Якщо вузли в одному компоненті, їхня парність мусить бути різною для дводольності
        return (rx.parity != ry.parity);
    }

    // Приєднуємо корінь rx до кореня ry та встановлюємо відносну парність
    dsu->parent[rx.root] = ry.root;
    dsu->parity[rx.root] = rx.parity ^ ry.parity ^ 1;
    return true;
}
