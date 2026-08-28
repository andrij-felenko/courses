#include <cstdint>
#include <array>

namespace capsicum {

inline constexpr uint32_t RightsVersion00 = 0;
inline constexpr uint32_t CurrentRightsVersion = RightsVersion00;

struct alignas(uint64_t) InternalRightsLayout {
    std::array<uint64_t, 2> raw_bits{};
};

} // namespace capsicum
