#include <cstdint>

class CurrentMonitor {
public:
    CurrentMonitor(uint16_t trip_current_ma = 580)
        : trip_threshold_ma_(trip_current_ma), adc_zero_(0), k_scale_fp_(0),
          overcurrent_ticks_(0), fault_latched_(false) {}

    template <typename AdcReader>
    void calibrateZero(AdcReader read_adc) {
        uint32_t sum = 0;
        constexpr uint16_t kSamples = 128;

        for (uint16_t i = 0; i < kSamples; ++i) {
            sum += read_adc();
        }
        adc_zero_ = static_cast<uint16_t>(sum / kSamples);
        overcurrent_ticks_ = 0;
        fault_latched_ = false;
    }

    void calibrateScale(uint16_t adc_cal, uint16_t ref_current_ma) {
        if (adc_cal > adc_zero_) {
            uint32_t span = adc_cal - adc_zero_;
            k_scale_fp_ = (static_cast<uint32_t>(ref_current_ma) << 16) / span;
        }
    }

    // Періодичне оновлення стану моніторингу (інтервал виклику 2 мс)
    bool update(uint16_t raw_adc) {
        if (fault_latched_) {
            return true;
        }

        uint16_t net_adc = (raw_adc > adc_zero_) ? static_cast<uint16_t>(raw_adc - adc_zero_) : 0;
        uint32_t current_ma = (static_cast<uint32_t>(net_adc) * k_scale_fp_) >> 16;

        if (current_ma >= trip_threshold_ma_) {
            if (++overcurrent_ticks_ >= 5) { // 5 тактів по 2 мс = 10 мс
                fault_latched_ = true;
                return true;
            }
        } else if (overcurrent_ticks_ > 0) {
            --overcurrent_ticks_;
        }

        return false;
    }

    void resetFault() {
        fault_latched_ = false;
        overcurrent_ticks_ = 0;
    }

    bool isFault() const { return fault_latched_; }

private:
    uint16_t trip_threshold_ma_;
    uint16_t adc_zero_;
    uint32_t k_scale_fp_;
    uint8_t  overcurrent_ticks_;
    bool     fault_latched_;
};
