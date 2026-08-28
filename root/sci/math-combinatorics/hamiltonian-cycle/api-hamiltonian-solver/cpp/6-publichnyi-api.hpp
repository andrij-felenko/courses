#ifndef LIBHAMILTONIAN_HPP
#define LIBHAMILTONIAN_HPP

#include <vector>
#include <optional>
#include <cstdint>
#include <chrono>
#include <span>

namespace hamiltonian {

class Graph {
public:
    explicit Graph(size_t vertices);
    ~Graph() = default;

    Graph(const Graph&) = delete;
    Graph& operator=(const Graph&) = delete;
    Graph(Graph&&) noexcept = default;
    Graph& operator=(Graph&&) noexcept = default;

    Status add_edge(size_t u, size_t v);
    [[nodiscard]] size_t num_vertices() const noexcept;
    [[nodiscard]] size_t num_edges() const noexcept;
    [[nodiscard]] bool has_edge(size_t u, size_t v) const noexcept;

    [[nodiscard]] bool check_dirac() const noexcept;
    [[nodiscard]] bool check_ore() const noexcept;

private:
    size_t vertices_;
    size_t edges_{0};
    std::vector<std::vector<uint8_t>> adj_;
};

class Solver {
public:
    explicit Solver(Config config = {});
    
    [[nodiscard]] Result solve(const Graph& graph) const;
    
private:
    Config config_;
};

} // namespace hamiltonian

#endif /* LIBHAMILTONIAN_HPP */
