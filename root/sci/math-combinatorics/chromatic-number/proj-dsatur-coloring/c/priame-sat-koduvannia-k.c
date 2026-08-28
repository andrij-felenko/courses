void export_dimacs_cnf(const Graph* g, int k, FILE* out) {
    int n = g->num_vertices;
    int num_vars = n * k;

    int num_edges = 0;
    for (int u = 0; u < n; ++u) {
        for (int v = u + 1; v < n; ++v) {
            if ((g->adj[u] & (1ULL << v)) != 0ULL) num_edges++;
        }
    }

    int at_least_one = n;
    int at_most_one = n * (k * (k - 1) / 2);
    int conflicts = num_edges * k;
    int total_clauses = at_least_one + at_most_one + conflicts;

    fprintf(out, "p cnf %d %d\n", num_vars, total_clauses);

    // 1. At-Least-One: кожен v має хоча б 1 колір
    for (int v = 0; v < n; ++v) {
        for (int c = 1; c <= k; ++c) {
            int var_id = v * k + c;
            fprintf(out, "%d ", var_id);
        }
        fprintf(out, "0\n");
    }

    // 2. At-Most-One: не більше 1 кольору на вершину
    for (int v = 0; v < n; ++v) {
        for (int c1 = 1; c1 <= k; ++c1) {
            for (int c2 = c1 + 1; c2 <= k; ++c2) {
                int var1 = v * k + c1;
                int var2 = v * k + c2;
                fprintf(out, "-%d -%d 0\n", var1, var2);
            }
        }
    }

    // 3. Конфлікти: ребра не можуть ділити колір c
    for (int u = 0; u < n; ++u) {
        for (int v = u + 1; v < n; ++v) {
            if ((g->adj[u] & (1ULL << v)) != 0ULL) {
                for (int c = 1; c <= k; ++c) {
                    int var_u = u * k + c;
                    int var_v = v * k + c;
                    fprintf(out, "-%d -%d 0\n", var_u, var_v);
                }
            }
        }
    }
}
