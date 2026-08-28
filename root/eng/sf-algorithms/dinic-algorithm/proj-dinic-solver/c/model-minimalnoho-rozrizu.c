#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

typedef struct {
    int num_projects;
    int64_t weights[MAX_VERTICES];
    DinicC solver;
} ProjectSelectorC;

void proj_init(ProjectSelectorC* ps, int n) {
    ps->num_projects = n;
    dinic_init(&ps->solver, n + 2);
}

void proj_set_weight(ProjectSelectorC* ps, int id, int64_t weight) {
    ps->weights[id] = weight;
}

void proj_add_dep(ProjectSelectorC* ps, int from, int to) {
    const int64_t inf = (int64_t)1e15;
    dinic_add_edge(&ps->solver, from, to, inf, 0);
}

int64_t proj_solve(ProjectSelectorC* ps) {
    int s = ps->num_projects;
    int t = ps->num_projects + 1;
    int64_t positive_sum = 0;

    for (int i = 0; i < ps->num_projects; ++i) {
        if (ps->weights[i] > 0) {
            dinic_add_edge(&ps->solver, s, i, ps->weights[i], 0);
            positive_sum += ps->weights[i];
        } else if (ps->weights[i] < 0) {
            dinic_add_edge(&ps->solver, i, t, -ps->weights[i], 0);
        }
    }

    int64_t min_cut = dinic_max_flow(&ps->solver, s, t);
    return positive_sum - min_cut;
}
