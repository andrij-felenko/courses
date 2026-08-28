#include <vector>
#include <utility>
#include <expected>

using EdgePair = std::pair<uint32_t, uint32_t>;

std::expected<std::vector<EdgePair>, WalkStatus> generate_ust_wilson(
    const GraphSpec& graph,
    uint32_t seed
);
