#include <string_view>
#include <span>
#include <cstdint>

namespace sys {

class bloom_filter_ops {
public:
    static void add(bloom_filter& bf, std::string_view key) noexcept {
        bf.add(std::span<const std::uint8_t>(reinterpret_cast<const std::uint8_t*>(key.data()), key.size()));
    }

    [[nodiscard]] static bool contains(const bloom_filter& bf, std::string_view key) noexcept {
        return bf.contains(std::span<const std::uint8_t>(reinterpret_cast<const std::uint8_t*>(key.data()), key.size()));
    }
};

} // namespace sys
