#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

typedef struct {
    int u;
    int v;
    int rank_u;
    int rank_v;
} DSUOp;

typedef struct {
    int *parent;
    int *rank;
    DSUOp *history;
    size_t history_top;
    size_t history_capacity;
    size_t num_sets;
} RollbackDSU;

RollbackDSU *rollback_dsu_create(size_t n, size_t max_ops) {
    RollbackDSU *dsu = (RollbackDSU *)malloc(sizeof(RollbackDSU));
    if (!dsu) return NULL;

    dsu->parent = (int *)malloc(n * sizeof(int));
    dsu->rank = (int *)calloc(n, sizeof(int));
    dsu->history = (DSUOp *)malloc(max_ops * sizeof(DSUOp));

    if (!dsu->parent || !dsu->rank || !dsu->history) {
        free(dsu->parent);
        free(dsu->rank);
        free(dsu->history);
        free(dsu);
        return NULL;
    }

    dsu->history_top = 0;
    dsu->history_capacity = max_ops;
    dsu->num_sets = n;
    for (size_t i = 0; i < n; i++) {
        dsu->parent[i] = (int)i;
    }
    return dsu;
}

void rollback_dsu_destroy(RollbackDSU *dsu) {
    if (!dsu) return;
    free(dsu->parent);
    free(dsu->rank);
    free(dsu->history);
    free(dsu);
}

// Без стиснення шляхів! Тільки ітеративний пошук кореня
int rollback_dsu_find(RollbackDSU *dsu, int x) {
    while (x != dsu->parent[x]) {
        x = dsu->parent[x];
    }
    return x;
}

bool rollback_dsu_union(RollbackDSU *dsu, int x, int y) {
    int root_x = rollback_dsu_find(dsu, x);
    int root_y = rollback_dsu_find(dsu, y);

    if (dsu->history_top >= dsu->history_capacity) return false;

    // Фіксуємо стан у стеку історії навіть при відсутності модифікацій
    dsu->history[dsu->history_top++] = (DSUOp){
        .u = root_x,
        .v = root_y,
        .rank_u = dsu->rank[root_x],
        .rank_v = dsu->rank[root_y]
    };

    if (root_x == root_y) return false;

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

void rollback_dsu_undo(RollbackDSU *dsu) {
    if (dsu->history_top == 0) return;

    DSUOp op = dsu->history[--dsu->history_top];
    if (op.u == op.v) return; // Модифікацій структури не було

    dsu->parent[op.u] = op.u;
    dsu->parent[op.v] = op.v;
    dsu->rank[op.u] = op.rank_u;
    dsu->rank[op.v] = op.rank_v;
    dsu->num_sets++;
}
