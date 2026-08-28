#include <cstdint>
#include <algorithm>
#include <concepts>

namespace sensor {

template <typename T = int32_t>
class FixedPointScaler {
public:
    // Масштабування відліку з формату Q16.16 з гарантованим захистом від переповнення
    [[nodiscard]] static constexpr T scale_and_clamp(int16_t raw_val, int32_t scale_q16, T min_val, T max_val) noexcept {
        const int64_t intermediate = static_cast<int64_t>(raw_val) * scale_q16;
        const auto rounded = static_cast<int32_t>((intermediate + (1LL << 15)) >> 16);
        return std::clamp(static_cast<T>(rounded), min_val, max_val);
    }
};

} // namespace sensor
