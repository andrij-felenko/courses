#include <cstdint>
#include <string_view>

namespace ribbon {

class Filter {
public:
    [[nodiscard]] bool Contains(std::uint64_t key) const noexcept;
    [[nodiscard]] bool Contains(std::string_view key) const noexcept;
};

} // namespace ribbon
