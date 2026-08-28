namespace graph::matching {

struct Edge {
    int u;
    int v;
    double weight{1.0};

    constexpr bool operator==(const Edge& other) const noexcept {
        return (u == other.u && v == other.v) || (u == other.v && v == other.u);
    }
};

struct Statistics {
    uint64_t num_augmentations{0};
    uint64_t num_blossoms_contracted{0};
    uint64_t num_lca_searches{0};
    double elapsed_milliseconds{0.0};
};

struct Result {
    size_t num_edges{0};
    double total_weight{0.0};
    std::vector<Edge> edges;
    std::vector<int> mate; // mate[u] містить індекс суміжної вершини або -1
    Statistics stats;
};

} // namespace graph::matching
