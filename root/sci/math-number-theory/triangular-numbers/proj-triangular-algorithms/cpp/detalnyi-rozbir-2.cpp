#include <iostream>
#include <cstddef>
#include <utility>
#include <algorithm>
#include <cstdint>

namespace math {

class CompleteGraphIndexer {
public:
    static constexpr std::size_t total_edges(std::size_t vertices) noexcept {
        return vertices * (vertices - 1) / 2;
    }

    static std::size_t get_edge_id(std::size_t u, std::size_t v) noexcept {
        if (u > v) std::swap(u, v);
        return v * (v - 1) / 2 + u;
    }

    static std::pair<std::size_t, std::size_t> get_vertices_from_edge_id(std::size_t edge_id) noexcept {
        const std::uint64_t disc = 8 * static_cast<std::uint64_t>(edge_id) + 1;
        
        std::uint64_t s = edge_id;
        std::uint64_t y = (s + 1) / 2;
        while (y < s) {
            s = y;
            y = (s + disc / s) / 2;
        }

        const std::size_t v = static_cast<std::size_t>((s - 1) / 2) + 1;
        const std::size_t u = edge_id - v * (v - 1) / 2;
        return {u, v};
    }
};

} // namespace math
