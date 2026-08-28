bool kempe_swap_chain(const Graph& g, std::vector<int>& colors, size_t start_v, int color_a, int color_b) {
    const size_t n = g.size();
    if (start_v >= n || (colors[start_v] != color_a && colors[start_v] != color_b)) {
        return false;
    }

    std::vector<bool> visited(n, false);
    std::vector<size_t> component;
    std::vector<size_t> queue;

    queue.push_back(start_v);
    visited[start_v] = true;

    size_t head = 0;
    while (head < queue.size()) {
        size_t u = queue[head++];
        component.push_back(u);

        for (size_t v = 0; v < n; ++v) {
            if ((g.neighbors(u) & (1ULL << v)) != 0ULL) {
                if (!visited[v] && (colors[v] == color_a || colors[v] == color_b)) {
                    visited[v] = true;
                    queue.push_back(v);
                }
            }
        }
    }

    for (size_t v : component) {
        if (colors[v] == color_a) colors[v] = color_b;
        else if (colors[v] == color_b) colors[v] = color_a;
    }

    return true;
}
