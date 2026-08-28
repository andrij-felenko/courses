#ifndef MATCHING_SOLVER_HPP
#define MATCHING_SOLVER_HPP

#include <vector>
#include <utility>
#include <cstdint>
#include <memory>
#include <system_error>
#include <expected>

namespace graph::matching {

enum class Algorithm {
    EdmondsBlossom, /**< General graph Edmonds Blossom algorithm O(V²E) */
    HopcroftKarp,   /**< Bipartite graph Hopcroft-Karp algorithm O(E√V) */
    LovaszRandom    /**< Algebraic randomized Tutte matrix determinant test O(nʷ) */
};

enum class ErrorCode {
    InvalidVertex = 1,
    NullPointer,
    OutOfMemory,
    NotBipartite,
    AlgorithmFailure
};

struct Edge {
    int32_t u;
    int32_t v;

    bool operator==(const Edge& other) const noexcept {
        return (u == other.u && v == other.v) || (u == other.v && v == other.u);
    }
};

struct MatchingResult {
    int32_t size{0};
    bool is_perfect{false};
    std::vector<Edge> edges;
};

class Graph {
public:
    explicit Graph(int32_t num_vertices);
    ~Graph();

    Graph(const Graph&) = delete;
    Graph& operator=(const Graph&) = delete;

    Graph(Graph&&) noexcept;
    Graph& operator=(Graph&&) noexcept;

    [[nodiscard]] int32_t num_vertices() const noexcept;
    
    std::expected<void, ErrorCode> add_edge(int32_t u, int32_t v);

    [[nodiscard]] std::expected<MatchingResult, ErrorCode> solve(
        Algorithm algo = Algorithm::EdmondsBlossom) const;

private:
    class Impl;
    std::unique_ptr<Impl> impl_;
};

} // namespace graph::matching

#endif /* MATCHING_SOLVER_HPP */
