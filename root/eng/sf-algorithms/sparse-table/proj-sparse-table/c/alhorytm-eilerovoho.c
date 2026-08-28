#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

typedef struct {
    size_t node_idx;
    int32_t depth;
} euler_entry_t;

typedef struct {
    size_t n;
    size_t *first_occ;
    euler_entry_t *euler_tour;
    sparse_table_t *st; /* Таблиця для мінімумів глибини */
} lca_solver_t;

/* LCA-запит за O(1) */
size_t lca_query(const lca_solver_t *solver, size_t u, size_t v) {
    size_t l = solver->first_occ[u];
    size_t r = solver->first_occ[v];
    if (l > r) { size_t tmp = l; l = r; r = tmp; }

    int32_t min_depth;
    st_query_min(solver->st, l, r, &min_depth);

    /* Знаходимо вузол із цією мінімальною глибиною */
    size_t k = (size_t)(31 - __builtin_clz((uint32_t)(r - l + 1)));
    size_t shift = (size_t)1 << k;

    int32_t d1 = solver->st->data[k * solver->st->n + l];
    int32_t d2 = solver->st->data[k * solver->st->n + (r - shift + 1)];

    if (d1 <= d2) {
        return solver->euler_tour[l].node_idx;
    } else {
        return solver->euler_tour[r - shift + 1].node_idx;
    }
}
