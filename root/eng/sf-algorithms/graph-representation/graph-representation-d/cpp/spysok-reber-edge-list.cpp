#include <cstdint>
#include <vector>
#include <compare>

struct Edge {
    uint32_t src;
    uint32_t dst;
    double weight;

    auto operator<=>(const Edge&) const = default;
};

std::vector<Edge> edge_list;
