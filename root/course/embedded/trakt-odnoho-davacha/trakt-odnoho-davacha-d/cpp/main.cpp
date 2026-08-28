#include <array>
#include <cstdint>
#include <optional>
#include <span>

namespace sensor {

struct CentiCelsius {
    int16_t value{0};

    [[nodiscard]] constexpr float to_celsius() const noexcept {
        return static_cast<float>(value) / 100.0f;
    }
};

class SignalChainProcessor {
public:
    static constexpr size_t kLutSize = 33;
    static constexpr uint32_t kStepShift = 7;
    static constexpr uint32_t kStepMask = (1 << kStepShift) - 1;
    static constexpr uint32_t kFilterShift = 4;

    constexpr explicit SignalChainProcessor(std::span<const int16_t, kLutSize> lut) noexcept
        : lut_(lut) {}

    void reset() noexcept {
        filter_acc_ = 0;
        initialized_ = false;
    }

    [[nodiscard]] std::optional<CentiCelsius> process(uint16_t raw_adc) noexcept {
        if (raw_adc > 4095) {
            raw_adc = 4095;
        }

        /* 1. Експоненційний IIR-фільтр */
        if (!initialized_) {
            filter_acc_ = static_cast<uint32_t>(raw_adc) << kFilterShift;
            initialized_ = true;
        } else {
            filter_acc_ = filter_acc_ + raw_adc - (filter_acc_ >> kFilterShift);
        }

        const auto filtered_code = static_cast<uint16_t>(filter_acc_ >> kFilterShift);

        /* 2. Таблична кусково-лінійна інтерполяція */
        const uint32_t idx = filtered_code >> kStepShift;
        const uint32_t rem = filtered_code & kStepMask;

        if (idx >= (kLutSize - 1)) {
            return CentiCelsius{lut_[kLutSize - 1]};
        }

        const int32_t t0 = lut_[idx];
        const int32_t t1 = lut_[idx + 1];
        const int32_t delta = t1 - t0;

        const int32_t interpolated = t0 + ((delta * static_cast<int32_t>(rem)) >> kStepShift);
        return CentiCelsius{static_cast<int16_t>(interpolated)};
    }

private:
    std::span<const int16_t, kLutSize> lut_;
    uint32_t filter_acc_{0};
    bool initialized_{false};
};

inline constexpr std::array<int16_t, SignalChainProcessor::kLutSize> kCalibrationLut = {
    -4000, -3200, -2500, -1900, -1400,  -960,  -560,  -200,
      130,   440,   740,  1030,  1320,  1610,  1900,  2200,
     2500,  2810,  3130,  3470,  3830,  4220,  4650,  5130,
     5680,  6320,  7090,  8040,  9260, 10900, 13200, 16500,
    20000
};

} // namespace sensor
