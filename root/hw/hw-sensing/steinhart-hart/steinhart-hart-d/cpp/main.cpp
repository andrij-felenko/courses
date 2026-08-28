#include <array>
#include <cmath>
#include <cstdint>
#include <concepts>
#include <optional>

namespace sensing {

struct SteinhartHartCoeffs {
    float a{1.130206e-3f};
    float b{2.339572e-4f};
    float c{8.828190e-8f};
};

template <size_t AdcBits = 12>
class NtcLinearizer {
public:
    static constexpr uint16_t MaxAdcCode = (1U << AdcBits) - 1U;

    constexpr explicit NtcLinearizer(float ref_resistance_ohms = 10000.0f,
                                    SteinhartHartCoeffs coeffs = {}) noexcept
        : r_ref_{ref_resistance_ohms}, coeffs_{coeffs} {}

    /*
     * Точний розрахунок за рівнянням Стейнгарта–Гарта
     */
    [[nodiscard]] std::optional<float> calculateTemperatureC(uint16_t raw_adc) const noexcept {
        if (raw_adc == 0 || raw_adc >= MaxAdcCode) {
            return std::nullopt; /* Вихід за межі вимірювального діапазону */
        }

        const float ratio = static_cast<float>(raw_adc) / (static_cast<float>(MaxAdcCode) - raw_adc);
        const float r_ntc = r_ref_ * ratio;

        const float ln_r = std::log(r_ntc);
        const float ln_r3 = ln_r * ln_r * ln_r;

        const float inv_t = coeffs_.a + (coeffs_.b * ln_r) + (coeffs_.c * ln_r3);
        return (1.0f / inv_t) - 273.15f;
    }

    /*
     * Таблична швидка цілочисельна інтерполяція (LUT)
     */
    [[nodiscard]] static constexpr int16_t calculateFastCentiCelsius(uint16_t raw_adc) noexcept {
        if (raw_adc >= MaxAdcCode) {
            return LutTable.back();
        }

        constexpr uint32_t ShiftBits = AdcBits - 5U; /* Для 12 біт: 12 - 5 = 7 (крок 128) */
        constexpr uint32_t RemainderMask = (1U << ShiftBits) - 1U;

        const uint32_t idx = raw_adc >> ShiftBits;
        const uint32_t rem = raw_adc & RemainderMask;

        const int32_t t_low  = LutTable[idx];
        const int32_t t_high = LutTable[idx + 1];

        const int32_t t_interp = t_low + (((t_high - t_low) * static_cast<int32_t>(rem)) >> ShiftBits);
        return static_cast<int16_t>(t_interp);
    }

private:
    float r_ref_;
    SteinhartHartCoeffs coeffs_;

    static constexpr std::array<int16_t, 33> LutTable = {
        -4500, -3812, -3154, -2520, -1908, -1314,  -736,  -172,
          381,   925,  1462,  1994,  2522,  3049,  3577,  4109,
     4648,  5196,  5757,  6334,  6932,  7556,  8212,  8908,
     9654, 10464, 11359, 12371, 13548, 14972, 16825, 19540,
        23000
    };
};

} // namespace sensing
