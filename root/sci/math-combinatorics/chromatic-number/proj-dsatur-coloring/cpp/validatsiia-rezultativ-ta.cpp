bool verify_coloring(const Graph& g, const ColoringResult& res) {
    const size_t n = g.size();
    for (size_t u = 0; u < n; ++u) {
        if (res.colors[u] <= 0) return false;
        for (size_t v = u + 1; v < n; ++v) {
            if ((g.neighbors(u) & (1ULL << v)) != 0ULL) {
                if (res.colors[u] == res.colors[v]) {
                    std::cerr << "Конфлікт: (" << u << ", " << v << ") колір " << res.colors[u] << "\n";
                    return false;
                }
            }
        }
    }
    return true;
}

Graph build_grotzsch_graph() {
    Graph g(11);
    for (size_t i = 0; i < 5; ++i) {
        g.add_edge(i, (i + 1) % 5);
    }
    for (size_t i = 0; i < 5; ++i) {
        size_t shadow = 5 + i;
        size_t left = (i + 4) % 5;
        size_t right = (i + 1) % 5;
        g.add_edge(shadow, left);
        g.add_edge(shadow, right);
    }
    for (size_t i = 5; i < 10; ++i) {
        g.add_edge(10, i);
    }
    return g;
}

int main() {
    std::cout << "=== Тестування точного розв'язувача DSATUR ===\n\n";

    Graph grotzsch = build_grotzsch_graph();
    ColoringResult wp = color_welsh_powell(grotzsch);
    ColoringResult ds = color_exact_solver(grotzsch);

    std::cout << "1. Граф Грьотча M4 (11 вершин, без трикутників):\n";
    std::cout << "   - Welsh-Powell:  хроматичне число = " << wp.chromatic_number 
              << " (кроків: " << wp.iterations << ", валідний: " 
              << (verify_coloring(grotzsch, wp) ? "ТАК" : "НІ") << ")\n";
    std::cout << "   - Точний DSATUR: хроматичне число = " << ds.chromatic_number 
              << " (кроків: " << ds.iterations << ", валідний: " 
              << (verify_coloring(grotzsch, ds) ? "ТАК" : "НІ") << ")\n";

    return 0;
}
