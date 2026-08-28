namespace graph::matching {

class MatchingSolver {
public:
    explicit MatchingSolver(size_t num_vertices, Mode mode = Mode::Cardinality, const std::optional<Allocator>& alloc = std::nullopt);
    ~MatchingSolver() noexcept;

    MatchingSolver(const MatchingSolver&) = delete;
    MatchingSolver& operator=(const MatchingSolver&) = delete;

    MatchingSolver(MatchingSolver&&) noexcept;
    MatchingSolver& operator=(MatchingSolver&&) noexcept;

    void add_edge(int u, int v, double weight = 1.0);
    void reserve_edges(size_t num_edges);

    [[nodiscard]] Result solve();
    [[nodiscard]] size_t num_vertices() const noexcept;
    [[nodiscard]] size_t num_edges() const noexcept;

    void clear() noexcept;

private:
    class Impl;
    std::unique_ptr<Impl> impl_;
};

} // namespace graph::matching
