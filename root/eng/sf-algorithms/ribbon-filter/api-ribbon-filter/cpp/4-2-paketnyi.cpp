#include <span>
#include <cstdint>
#include <vector>

namespace ribbon {

class Filter {
public:
    void ContainsBatch(std::span<const std::uint64_t> keys,
                       std::span<bool> out_results) const noexcept;
};

} // namespace ribbon
