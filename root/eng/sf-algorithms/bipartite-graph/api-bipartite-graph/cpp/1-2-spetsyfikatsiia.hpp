// C++ API: Інкапсульований клас двочасткового графа
#ifndef BIPARTITE_GRAPH_HPP
#define BIPARTITE_GRAPH_HPP

#include <vector>
#include <cstddef>
#include <stdexcept>
#include <optional>
#include <span>

namespace net {

enum class Status {
    Ok = 0,
    NotBipartite = -1,
    InvalidPartition = -2,
    IndexOutOfBounds = -3,
    NullPointer = -4,
    NoMemory = -5
};

class BipartiteGraph {
public:
    BipartiteGraph(std::size_t num_left, std::size_t num_right);
    ~BipartiteGraph() = default;

    BipartiteGraph(const BipartiteGraph&) = default;
    BipartiteGraph& operator=(const BipartiteGraph&) = default;
    BipartiteGraph(BipartiteGraph&&) noexcept = default;
    BipartiteGraph& operator=(BipartiteGraph&&) noexcept = default;

    void add_edge(std::size_t u_left, std::size_t v_right);

    [[nodiscard]] std::size_t num_left() const noexcept { return num_left_; }
    [[nodiscard]] std::size_t num_right() const noexcept { return num_right_; }
    [[nodiscard]] std::size_t num_edges() const noexcept { return num_edges_; }

    [[nodiscard]] std::span<const std::size_t> neighbors_left(std::size_t u) const;
    [[nodiscard]] std::span<const std::size_t> neighbors_right(std::size_t v) const;

private:
    std::size_t num_left_;
    std::size_t num_right_;
    std::size_t num_edges_{0};
    std::vector<std::vector<std::size_t>> adj_left_;
    std::vector<std::vector<std::size_t>> adj_right_;
};

} // namespace net

#endif // BIPARTITE_GRAPH_HPP
