ColoringResult color_welsh_powell(const Graph& g) {
    ColoringResult res;
    const size_t n = g.size();
    res.colors.assign(n, -1);
    res.iterations = 0;

    std::vector<size_t> order(n);
    std::iota(order.begin(), order.end(), 0);
    std::sort(order.begin(), order.end(), [&g](size_t a, size_t b) {
        return g.degree(a) > g.degree(b);
    });

    size_t colored_count = 0;
    int current_color = 1;

    while (colored_count < n) {
        uint64_t current_color_set = 0ULL;
        for (size_t v : order) {
            res.iterations++;
            if (res.colors[v] == -1) {
                if ((g.neighbors(v) & current_color_set) == 0ULL) {
                    res.colors[v] = current_color;
                    current_color_set |= (1ULL << v);
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
