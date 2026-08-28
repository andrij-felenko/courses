bool verify_coloring(const Graph* g, const ColoringResult* res) {
    int n = g->num_vertices;
    for (int u = 0; u < n; ++u) {
        if (res->colors[u] <= 0) return false;
        for (int v = u + 1; v < n; ++v) {
            if ((g->adj[u] & (1ULL << v)) != 0ULL) {
                if (res->colors[u] == res->colors[v]) {
                    printf("Помилка! Конфлікт між вершинами %d та %d (колір %d)\n", u, v, res->colors[u]);
                    return false;
                }
            }
        }
    }
    return true;
}

Graph build_grotzsch_graph(void) {
    Graph g;
    graph_init(&g, 11);
    for (int i = 0; i < 5; ++i) {
        graph_add_edge(&g, i, (i + 1) % 5);
    }
    for (int i = 0; i < 5; ++i) {
        int v_shadow = 5 + i;
        int left = (i + 4) % 5;
        int right = (i + 1) % 5;
        graph_add_edge(&g, v_shadow, left);
        graph_add_edge(&g, v_shadow, right);
    }
    for (int i = 5; i < 10; ++i) {
        graph_add_edge(&g, 10, i);
    }
    return g;
}

int main(void) {
    printf("=== Тестування точного розв'язувача DSATUR ===\n\n");

    Graph grotzsch = build_grotzsch_graph();
    ColoringResult wp = color_welsh_powell(&grotzsch);
    ColoringResult ds = color_exact_solver(&grotzsch);

    printf("1. Граф Грьотча M4 (11 вершин, без трикутників):\n");
    printf("   - Welsh-Powell:  хроматичне число = %d (кроків: %llu, валідний: %s)\n",
           wp.chromatic_number, (unsigned long long)wp.iterations, verify_coloring(&grotzsch, &wp) ? "ТАК" : "НІ");
    printf("   - Точний DSATUR: хроматичне число = %d (кроків: %llu, валідний: %s)\n",
           ds.chromatic_number, (unsigned long long)ds.iterations, verify_coloring(&grotzsch, &ds) ? "ТАК" : "НІ");

    return 0;
}
