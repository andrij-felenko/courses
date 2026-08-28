// C++20 API: Переліки та структури результату
namespace graph::matching {

enum class Status {
    Success = 0,
    NullPointer = -1,
    InvalidIndex = -2,
    OutOfMemory = -3,
    InvalidGraph = -4
};

enum class Algorithm {
    Kuhn = 0,
    HopcroftKarp = 1,
    Dinic = 2
};

struct MatchingSolution {
    std::size_t matching_size{0};
    std::vector<int> match_u; // match_u[u] = v або -1
    std::vector<int> match_v; // match_v[v] = u або -1
    std::vector<bool> min_vertex_cover_u;
    std::vector<bool> min_vertex_cover_v;
    double execution_time_ms{0.0};
};

class BipartiteMatchingSolver {
public:
    explicit BipartiteMatchingSolver(std::size_t u_size, std::size_t v_size);
    ~BipartiteMatchingSolver() noexcept = default;

    BipartiteMatchingSolver(const BipartiteMatchingSolver&) = delete;
    BipartiteMatchingSolver& operator=(const BipartiteMatchingSolver&) = delete;
    BipartiteMatchingSolver(BipartiteMatchingSolver&&) noexcept = default;
    BipartiteMatchingSolver& operator=(BipartiteMatchingSolver&&) noexcept = default;

    void add_edge(std::size_t u, std::size_t v);
    void clear_edges() noexcept;
    [[nodiscard]] MatchingSolution solve(Algorithm algo = Algorithm::HopcroftKarp) const;

    [[nodiscard]] std::size_t u_size() const noexcept;
    [[nodiscard]] std::size_t v_size() const noexcept;
    [[nodiscard]] std::size_t edge_count() const noexcept;

private:
    struct Impl;
    std::unique_ptr<Impl> impl_;
};

} // namespace graph::matching
