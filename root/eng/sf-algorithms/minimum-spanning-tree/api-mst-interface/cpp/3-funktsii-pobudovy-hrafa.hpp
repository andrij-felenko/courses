namespace mst {

class Graph {
public:
    explicit Graph(size_t num_vertices);
    ~Graph();

    Graph(const Graph&) = delete;
    Graph& operator=(const Graph&) = delete;

    Graph(Graph&&) noexcept;
    Graph& operator=(Graph&&) noexcept;

    [[nodiscard]] StatusCode add_edge(int32_t u, int32_t v, int64_t weight) noexcept;
    [[nodiscard]] StatusCode add_edges(std::span<const EdgeDesc> edges) noexcept;

    [[nodiscard]] size_t vertex_count() const noexcept;
    [[nodiscard]] size_t edge_count() const noexcept;

private:
    struct Impl;
    std::unique_ptr<Impl> impl_;
};

} // namespace mst
