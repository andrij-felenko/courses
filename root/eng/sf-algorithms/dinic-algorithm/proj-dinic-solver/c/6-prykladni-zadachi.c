#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

typedef struct {
    int n_left;
    int n_right;
    DinicC solver;
} BipartiteMatchingC;

void bpm_init(BipartiteMatchingC* bpm, int l, int r) {
    bpm->n_left = l;
    bpm->n_right = r;
    dinic_init(&bpm->solver, l + r + 2);
}

void bpm_add_edge(BipartiteMatchingC* bpm, int u, int v) {
    dinic_add_edge(&bpm->solver, u + 1, bpm->n_left + 1 + v, 1, 0);
}

int bpm_solve(BipartiteMatchingC* bpm) {
    int s = 0;
    int t = bpm->n_left + bpm->n_right + 1;

    for (int i = 0; i < bpm->n_left; ++i) {
        dinic_add_edge(&bpm->solver, s, i + 1, 1, 0);
    }
    for (int j = 0; j < bpm->n_right; ++j) {
        dinic_add_edge(&bpm->solver, bpm->n_left + 1 + j, t, 1, 0);
    }

    return (int)dinic_max_flow(&bpm->solver, s, t);
}
