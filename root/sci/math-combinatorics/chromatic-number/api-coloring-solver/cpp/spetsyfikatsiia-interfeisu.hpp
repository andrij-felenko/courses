#ifndef COLORING_SOLVER_HPP
#define COLORING_SOLVER_HPP

#include <cstdint>
#include <cstddef>
#include <string>
#include <string_view>
#include <vector>
#include <span>
#include <memory>
#include <expected>
#include <optional>
#include <chrono>

namespace coloring {

enum class ErrorCode : int32_t {
    Ok = 0,
    InvalidArgument = -1,
    VertexOutOfBounds = -2,
    SelfLoopDetected = -3,
    PinnedConflict = -4,
    OutOfMemory = -5,
    Timeout = -6,
    TargetInfeasible = -7,
    InvalidCertificate = -8,
    IoFailure = -9,
    SolverDiverged = -10
};

enum class Status : int32_t {
    Unsolved = 0,
    Optimal = 1,
    Feasible = 2,
    Infeasible = 3,
    Timeout = 4
};

enum class Engine : int32_t {
    GreedyDsatur = 0,
    ExactDsatur = 1,
    Ilp = 2,
    BranchAndPrice = 3
};

enum class CertificateType : int32_t {
    None = 0,
    MaxClique = 1,
    ExhaustiveTree = 2,
    DualBoundExhaustion = 3
};

struct Certificate {
    CertificateType type{CertificateType::None};
    std::vector<int32_t> vertices;
    uint64_t explored_nodes{0};
    uint64_t generated_columns{0};
    uint64_t simplex_iterations{0};
};

struct Result {
    Status status{Status::Unsolved};
    int32_t chromatic_number{0};
    std::vector<int32_t> colors;
    int32_t lower_bound{0};
    int32_t upper_bound{0};
    std::chrono::microseconds elapsed{0};
    Certificate certificate;
};

struct Diagnostics {
    ErrorCode last_error{ErrorCode::Ok};
    std::string message;
    int32_t conflict_u{-1};
    int32_t conflict_v{-1};
    size_t peak_memory_bytes{0};
};

struct SolverConfig {
    Engine engine{Engine::ExactDsatur};
    std::chrono::milliseconds time_limit{5000};
    std::optional<int32_t> lower_bound_hint;
    std::optional<int32_t> upper_bound_target;
    int32_t symmetry_breaking_level{2};
    bool enable_kempe_pass{true};
    uint32_t random_seed{42};
    size_t memory_limit_bytes{1024 * 1024 * 1024}; /* 1 ГБ */
};

class Graph {
public:
    explicit Graph(int32_t num_vertices);
    ~Graph() = default;

    Graph(const Graph&) = default;
    Graph& operator=(const Graph&) = default;
    Graph(Graph&&) noexcept = default;
    Graph& operator=(Graph&&) noexcept = default;

    [[nodiscard]] int32_t vertex_count() const noexcept { return num_vertices_; }
    [[nodiscard]] int32_t edge_count() const noexcept { return num_edges_; }

    [[nodiscard]] std::expected<void, ErrorCode> add_edge(int32_t u, int32_t v) noexcept;
    [[nodiscard]] std::expected<void, ErrorCode> pin_color(int32_t v, int32_t color) noexcept;
    [[nodiscard]] bool has_edge(int32_t u, int32_t v) const noexcept;
    [[nodiscard]] std::optional<int32_t> get_pinned_color(int32_t v) const noexcept;

    [[nodiscard]] std::span<const uint64_t> adjacency_row(int32_t v) const noexcept;

private:
    int32_t num_vertices_{0};
    int32_t num_edges_{0};
    size_t row_words_{0};
    std::vector<uint64_t> adj_matrix_;
    std::vector<int32_t> pinned_colors_;
};

class Solver {
public:
    explicit Solver(SolverConfig config = SolverConfig{});
    ~Solver() = default;

    [[nodiscard]] std::expected<Result, Diagnostics> solve(const Graph& graph) const;
    [[nodiscard]] static std::expected<void, Diagnostics> verify(const Graph& graph, const Result& result);

    [[nodiscard]] static std::expected<Graph, Diagnostics> import_dimacs(std::string_view filepath);
    [[nodiscard]] static std::expected<void, Diagnostics> export_dimacs(std::string_view filepath, const Graph& graph);
    [[nodiscard]] static std::expected<void, Diagnostics> export_json(
        std::string_view filepath,
        const Graph& graph,
        const Result& result
    );

private:
    SolverConfig config_;
};

} // namespace coloring

#endif /* COLORING_SOLVER_HPP */
