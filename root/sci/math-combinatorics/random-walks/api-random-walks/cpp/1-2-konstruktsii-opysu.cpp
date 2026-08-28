#include <cstdint>
#include <span>
#include <optional>

struct GraphSpec {
    uint32_t num_vertices{0};
    uint64_t num_edges{0};
    bool is_directed{false};
    std::span<const uint32_t> row_ptr{};
    std::span<const uint32_t> col_idx{};
    std::optional<std::span<const double>> weights{std::nullopt};
};
