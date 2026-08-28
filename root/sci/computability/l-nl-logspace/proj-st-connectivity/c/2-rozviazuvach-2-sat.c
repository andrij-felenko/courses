/* C11 implementation: 2-SAT Satisfiability Checker via Implication Graph */
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>

typedef struct {
    int var1; /* Positive for x_i, negative for -x_i */
    int var2;
} Clause2SAT;

typedef struct {
    uint32_t num_vars;
    uint32_t num_clauses;
    const Clause2SAT *clauses;
} Formula2SAT;

/* Maps literal to vertex index in range [0 .. 2*num_vars - 1] */
static inline uint32_t literal_to_vertex(int lit, uint32_t num_vars) {
    if (lit > 0) {
        return (uint32_t)(lit - 1);
    } else {
        return (uint32_t)(-lit - 1) + num_vars;
    }
}

/* Returns negated literal vertex index */
static inline uint32_t negated_literal_vertex(int lit, uint32_t num_vars) {
    return literal_to_vertex(-lit, num_vars);
}

/* Checks if implication edge (u -> v) exists dynamically without allocating adjacency matrix */
static bool has_implication_edge(const Formula2SAT *f, uint32_t u, uint32_t v) {
    for (uint32_t i = 0; i < f->num_clauses; ++i) {
        int a = f->clauses[i].var1;
        int b = f->clauses[i].var2;

        /* (a v b) is equivalent to (-a -> b) and (-b -> a) */
        uint32_t not_a = negated_literal_vertex(a, f->num_vars);
        uint32_t pos_b = literal_to_vertex(b, f->num_vars);
        uint32_t not_b = negated_literal_vertex(b, f->num_vars);
        uint32_t pos_a = literal_to_vertex(a, f->num_vars);

        if ((u == not_a && v == pos_b) || (u == not_b && v == pos_a)) {
            return true;
        }
    }
    return false;
}

/* Savitch-style reachability check over virtual implication graph */
static bool impl_can_reach(const Formula2SAT *f, uint32_t u, uint32_t v, uint32_t steps) {
    if (u == v) return true;
    if (steps == 1) return has_implication_edge(f, u, v);

    uint32_t total_nodes = 2 * f->num_vars;
    uint32_t half_steps = (steps + 1) / 2;

    for (uint32_t w = 0; w < total_nodes; ++w) {
        if (impl_can_reach(f, u, w, half_steps)) {
            if (impl_can_reach(f, w, v, steps - half_steps)) {
                return true;
            }
        }
    }
    return false;
}

/* Evaluates if 2-SAT formula is satisfiable in O(log^2 N) space */
bool is_2sat_satisfiable(const Formula2SAT *f) {
    uint32_t total_nodes = 2 * f->num_vars;

    for (uint32_t i = 1; i <= f->num_vars; ++i) {
        uint32_t pos_v = literal_to_vertex((int)i, f->num_vars);
        uint32_t neg_v = negated_literal_vertex((int)i, f->num_vars);

        /* Check if x_i -> -x_i and -x_i -> x_i both exist */
        if (impl_can_reach(f, pos_v, neg_v, total_nodes) &&
            impl_can_reach(f, neg_v, pos_v, total_nodes)) {
            return false; /* Unsatisfiable due to contradiction cycle */
        }
    }
    return true;
}

int main(void) {
    /* Formula: (x1 v x2) ^ (-x1 v x2) ^ (x1 v -x2) ^ (-x1 v -x2) -> Unsatisfiable */
    const Clause2SAT clauses[] = {
        {  1,  2 },
        { -1,  2 },
        {  1, -2 },
        { -1, -2 }
    };
    Formula2SAT f = {
        .num_vars = 2,
        .num_clauses = 4,
        .clauses = clauses
    };

    bool sat = is_2sat_satisfiable(&f);
    printf("2-SAT Formula is %s\n", sat ? "SATISFIABLE" : "UNSATISFIABLE");

    return 0;
}
