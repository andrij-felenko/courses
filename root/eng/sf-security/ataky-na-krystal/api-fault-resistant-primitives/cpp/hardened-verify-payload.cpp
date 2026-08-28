#include <cstdint>
#include <cstddef>
#include <span>

namespace sec {

class HardenedVerifier {
public:
    [[nodiscard]] static Token verify(std::span<const std::uint8_t> computed,
                                      std::span<const std::uint8_t> expected,
                                      std::uint32_t entropy) noexcept;
};

} // namespace sec
