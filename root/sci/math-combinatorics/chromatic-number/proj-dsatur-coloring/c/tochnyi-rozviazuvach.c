typedef struct {
    int colors[MAX_VERTICES];
    uint64_t neighbor_colors[MAX_VERTICES];
    int sat_deg[MAX_VERTICES];
    int uncolored_deg[MAX_VERTICES];
    int best_colors[MAX_VERTICES];
    int best_k;
    uint64_t search_steps;
} DSATURState;

static int choose_next_vertex(const DSATURState* state, int n) {
    int best_v = -1;
    int max_sat = -1;
    int max_deg = -1;

    for (int v = 0; v < n; ++v) {
        if (state->colors[v] == 0) {
            if (state->sat_deg[v] > max_sat || 
               (state->sat_deg[v] == max_sat && state->uncolored_deg[v] > max_deg)) {
                max_sat = state->sat_deg[v];
                max_deg = state->uncolored_deg[v];
                best_v = v;
            }
        }
    }
    return best_v;
}

ColoringResult color_dsatur_heuristic(const Graph* g) {
    ColoringResult res;
    int n = g->num_vertices;
    res.iterations = 0;
    res.chromatic_number = 0;

    DSATURState st;
    memset(&st, 0, sizeof(st));

    for (int i = 0; i < n; ++i) {
        st.uncolored_deg[i] = __builtin_popcountll(g->adj[i]);
    }

    int max_color_used = 0;
    for (int step = 0; step < n; ++step) {
        res.iterations++;
        int v = choose_next_vertex(&st, n);
        if (v == -1) break;

        int c = 1;
        while ((st.neighbor_colors[v] & (1ULL << c)) != 0ULL) {
            c++;
        }

        st.colors[v] = c;
        if (c > max_color_used) max_color_used = c;

        for (int u = 0; u < n; ++u) {
            if ((g->adj[v] & (1ULL << u)) != 0ULL && st.colors[u] == 0) {
                if ((st.neighbor_colors[u] & (1ULL << c)) == 0ULL) {
                    st.neighbor_colors[u] |= (1ULL << c);
                    st.sat_deg[u]++;
                }
                st.uncolored_deg[u]--;
            }
        }
    }

    for (int i = 0; i < n; ++i) res.colors[i] = st.colors[i];
    res.chromatic_number = max_color_used;
    res.is_valid = true;
    return res;
}

static void dsatur_backtrack(const Graph* g, DSATURState* st, int colored_count, int current_max_k) {
    st->search_steps++;
    int n = g->num_vertices;

    if (colored_count == n) {
        if (current_max_k < st->best_k) {
            st->best_k = current_max_k;
            memcpy(st->best_colors, st->colors, sizeof(int) * n);
        }
        return;
    }

    if (current_max_k >= st->best_k) {
        return;
    }

    int v = choose_next_vertex(st, n);
    if (v == -1) return;

    for (int c = 1; c <= current_max_k + 1 && c < st->best_k; ++c) {
        if ((st->neighbor_colors[v] & (1ULL << c)) == 0ULL) {
            uint64_t old_mask = st->neighbor_colors[v];
            st->colors[v] = c;

            int changed_neighbors[MAX_VERTICES];
            int changed_count = 0;

            for (int u = 0; u < n; ++u) {
                if ((g->adj[v] & (1ULL << u)) != 0ULL && st->colors[u] == 0) {
                    st->uncolored_deg[u]--;
                    if ((st->neighbor_colors[u] & (1ULL << c)) == 0ULL) {
                        st->neighbor_colors[u] |= (1ULL << c);
                        st->sat_deg[u]++;
                        changed_neighbors[changed_count++] = u;
                    }
                }
            }

            int next_max_k = (c > current_max_k) ? c : current_max_k;
            dsatur_backtrack(g, st, colored_count + 1, next_max_k);

            st->colors[v] = 0;
            st->neighbor_colors[v] = old_mask;
            for (int i = 0; i < changed_count; ++i) {
                int u = changed_neighbors[i];
                st->neighbor_colors[u] &= ~(1ULL << c);
                st->sat_deg[u]--;
            }
            for (int u = 0; u < n; ++u) {
                if ((g->adj[v] & (1ULL << u)) != 0ULL && st->colors[u] == 0) {
                    st->uncolored_deg[u]++;
                }
            }
        }
    }
}

ColoringResult color_exact_solver(const Graph* g) {
    ColoringResult heur = color_dsatur_heuristic(g);

    DSATURState st;
    memset(&st, 0, sizeof(st));
    st.best_k = heur.chromatic_number;
    memcpy(st.best_colors, heur.colors, sizeof(int) * g->num_vertices);
    st.search_steps = 0;

    int n = g->num_vertices;
    for (int i = 0; i < n; ++i) {
        st.uncolored_deg[i] = __builtin_popcountll(g->adj[i]);
    }

    dsatur_backtrack(g, &st, 0, 0);

    ColoringResult res;
    res.chromatic_number = st.best_k;
    res.iterations = st.search_steps;
    res.is_valid = true;
    for (int i = 0; i < n; ++i) res.colors[i] = st.best_colors[i];
    return res;
}
