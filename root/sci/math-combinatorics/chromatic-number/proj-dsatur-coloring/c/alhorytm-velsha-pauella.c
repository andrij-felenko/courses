ColoringResult color_welsh_powell(const Graph* g) {
    ColoringResult res;
    res.chromatic_number = 0;
    res.iterations = 0;
    res.is_valid = false;
    int n = g->num_vertices;
    for (int i = 0; i < n; ++i) res.colors[i] = -1;

    int order[MAX_VERTICES];
    int degrees[MAX_VERTICES];
    for (int i = 0; i < n; ++i) {
        order[i] = i;
        degrees[i] = __builtin_popcountll(g->adj[i]);
    }

    // Сортування вершин за спаданням степеня
    for (int i = 0; i < n - 1; ++i) {
        for (int j = i + 1; j < n; ++j) {
            if (degrees[order[j]] > degrees[order[i]]) {
                int tmp = order[i];
                order[i] = order[j];
                order[j] = tmp;
            }
        }
    }

    int colored_count = 0;
    int current_color = 1;

    while (colored_count < n) {
        uint64_t current_color_mask = 0ULL;
        for (int i = 0; i < n; ++i) {
            res.iterations++;
            int v = order[i];
            if (res.colors[v] == -1) {
                if ((g->adj[v] & current_color_mask) == 0ULL) {
                    res.colors[v] = current_color;
                    current_color_mask |= (1ULL << v);
                    colored_count++;
                }
            }
        }
        current_color++;
    }

    res.chromatic_number = current_color - 1;
    res.is_valid = true;
    return res;
}
