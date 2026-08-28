void export_dimacs_cnf(const Graph& g, int k, std::ostream& out) {
    const size_t n = g.size();
    const size_t num_vars = n * k;

    size_t num_edges = 0;
    for (size_t u = 0; u < n; ++u) {
        for (size_t v = u + 1; v < n; ++v) {
            if ((g.neighbors(u) & (1ULL << v)) != 0ULL) num_edges++;
        }
    }

    size_t total_clauses = n + n * (k * (k - 1) / 2) + num_edges * k;

    out << "p cnf " << num_vars << " " << total_clauses << "\n";

    for (size_t v = 0; v < n; ++v) {
        for (int c = 1; c <= k; ++c) {
            out << (v * k + c) << " ";
        }
        out << "0\n";
    }

    for (size_t v = 0; v < n; ++v) {
        for (int c1 = 1; c1 <= k; ++c1) {
            for (int c2 = c1 + 1; c2 <= k; ++c2) {
                out << "-" << (v * k + c1) << " -" << (v * k + c2) << " 0\n";
            }
        }
    }

    for (size_t u = 0; u < n; ++u) {
        for (size_t v = u + 1; v < n; ++v) {
            if ((g.neighbors(u) & (1ULL << v)) != 0ULL) {
                for (int c = 1; c <= k; ++c) {
                    out << "-" << (u * k + c) << " -" << (v * k + c) << " 0\n";
                }
            }
        }
    }
}
