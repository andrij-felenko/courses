bool kempe_swap_chain(const Graph* g, int* colors, int start_v, int color_a, int color_b) {
    int n = g->num_vertices;
    if (colors[start_v] != color_a && colors[start_v] != color_b) return false;

    bool visited[MAX_VERTICES];
    memset(visited, 0, sizeof(visited));

    int queue[MAX_VERTICES];
    int head = 0, tail = 0;

    queue[tail++] = start_v;
    visited[start_v] = true;

    // BFS для виділення зв'язної компоненти кольорів {color_a, color_b}
    while (head < tail) {
        int u = queue[head++];
        for (int v = 0; v < n; ++v) {
            if ((g->adj[u] & (1ULL << v)) != 0ULL) {
                if (!visited[v] && (colors[v] == color_a || colors[v] == color_b)) {
                    visited[v] = true;
                    queue[tail++] = v;
                }
            }
        }
    }

    // Інверсія кольорів у виділеній компоненті
    for (int i = 0; i < tail; ++i) {
        int v = queue[i];
        if (colors[v] == color_a) colors[v] = color_b;
        else if (colors[v] == color_b) colors[v] = color_a;
    }

    return true;
}
