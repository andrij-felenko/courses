#include <cstdint>
#include <cstddef>
#include <vector>
#include <optional>
#include <span>

enum class VersionCompareResult {
    Equal,
    Dominates,
    Dominated,
    Concurrent
};

struct VersionEntry {
    uint32_t node_id{0};
    uint64_t counter{0};

    auto operator<=>(const VersionEntry&) const = default;
};

struct Dot {
    uint32_t node_id{0};
    uint64_t counter{0};

    auto operator<=>(const Dot&) const = default;
};

class VersionVector {
public:
    uint16_t flags{0};
    std::optional<Dot> dot;
    std::vector<VersionEntry> entries;

    [[nodiscard]] bool is_pruned() const noexcept {
        return (flags & 0x0001) != 0;
    }
};
