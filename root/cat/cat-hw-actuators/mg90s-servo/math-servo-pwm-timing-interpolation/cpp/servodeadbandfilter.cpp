#include <cstdint>
#include <algorithm>
#include <cmath>

class ServoDeadbandFilter {
public:
    static constexpr uint16_t kMinPulseUs = 500;
    static constexpr uint16_t kMaxPulseUs = 2500;
    static constexpr uint16_t kDefaultDeadbandUs = 4;

    explicit ServoDeadbandFilter(uint16_t initial_pulse_us = 1500, uint16_t deadband_us = kDefaultDeadbandUs)
        : current_pulse_us_(std::clamp(initial_pulse_us, kMinPulseUs, kMaxPulseUs)),
          deadband_us_(deadband_us) {}

    /* Повертає true та оновлює pulse_out лише при подоланні зони нечутливості */
    bool update(uint16_t target_pulse_us, uint16_t& pulse_out) {
        const uint16_t clamped_target = std::clamp(target_pulse_us, kMinPulseUs, kMaxPulseUs);
        const int32_t diff = static_cast<int32_t>(clamped_target) - static_cast<int32_t>(current_pulse_us_);

        if (std::abs(diff) >= deadband_us_) {
            current_pulse_us_ = clamped_target;
            pulse_out = current_pulse_us_;
            return true; /* Записуємо нове значення в апаратний регістр CCR */
        }

        pulse_out = current_pulse_us_;
        return false; /* Ігноруємо мікроколивання для усунення тремтіння */
    }

    uint16_t current_pulse() const { return current_pulse_us_; }

private:
    uint16_t current_pulse_us_;
    uint16_t deadband_us_;
};
