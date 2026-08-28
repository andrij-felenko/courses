#include <array>
#include <cstdint>
#include <expected>
#include <optional>
#include <span>

namespace sensor {

enum class SensorError : uint8_t {
    OpenCircuit,
    ShortCircuit,
    InvalidInput
};

struct FixedTemp {
    int32_t raw_q16{0};

    [[nodiscard]] constexpr float to_float() const noexcept {
        return static_cast<float>(raw_q16) / 65536.0f;
    }

    [[nodiscard]] constexpr int32_t to_centicelsius() const noexcept {
        return (raw_q16 * 100 + (1 << 15)) >> 16;
    }
};

class NtcInterpolator {
public:
    static constexpr size_t kLutSize = 33;
    static constexpr uint32_t kStepShift = 7;
    static constexpr uint32_t kStepMask = (1 << kStepShift) - 1;

    constexpr explicit NtcInterpolator(std::span<const int32_t, kLutSize> table) noexcept
        : lut_(table) {}

    [[nodiscard]] constexpr std::expected<FixedTemp, SensorError> lookup(uint16_t adc_raw) const noexcept {
        if (adc_raw < 30) {
            return std::unexpected(SensorError::OpenCircuit);
        }
        if (adc_raw >= 4080) {
            return std::unexpected(SensorError::ShortCircuit);
        }

        if (adc_raw > 4095) {
            adc_raw = 4095;
        }

        const uint32_t idx = adc_raw >> kStepShift;
        const uint32_t rem = adc_raw & kStepMask;

        if (idx >= (kLutSize - 1)) {
            return FixedTemp{lut_[kLutSize - 1]};
        }

        const int32_t t0 = lut_[idx];
        const int32_t t1 = lut_[idx + 1];
        const int32_t delta = t1 - t0;

        const int32_t interpolated = t0 + ((delta * static_cast<int32_t>(rem)) >> kStepShift);
        return FixedTemp{interpolated};
    }

private:
    std::span<const int32_t, kLutSize> lut_;
};

/* Зразок таблиці з можливістю генерації на етапі компіляції */
inline constexpr std::array<int32_t, NtcInterpolator::kLutSize> kDefaultNtcTable = {
    -2621440, -2097152, -1638400, -1245184,  -917504,  -629145,  -367001,  -131072,
       85196,   288358,   484966,   675020,   865075,  1055129,  1245184,  1441792,
     1638400,  1841561,  2051276,  2274099,  2510028,  2765619,  3047424,  3361996,
     3722444,  4141875,  4646502,  5269094,  6068633,  7143424,  8650752, 10813440,
    13107200
};

} // namespace sensor
