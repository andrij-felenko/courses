#include <span>
#include <cstdint>
#include <vector>
#include <optional>

namespace ribbon {

class Filter {
public:
    [[nodiscard]] std::vector<std::uint8_t> Serialize() const;
    static std::optional<Filter> OpenZeroCopy(std::span<const std::uint8_t> mapped_bytes);
};

} // namespace ribbon
