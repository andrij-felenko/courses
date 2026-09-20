#include <Arduino.h>

class AxisCalibrator {
private:
    static constexpr size_t SAMPLE_COUNT = 64;
    uint16_t raw_zero_ = 2048;
    uint16_t raw_min_ = 0;
    uint16_t raw_max_ = 4095;
    float scale_neg_ = 1.0f / 2048.0f;
    float scale_pos_ = 1.0f / 2047.0f;
    bool calibrated_ = false;

public:
    AxisCalibrator(uint16_t r_min, uint16_t r_max) : raw_min_(r_min), raw_max_(r_max) {}

    bool calibrateZero(const uint16_t samples[SAMPLE_COUNT], float max_variance) {
        uint32_t sum = 0;
        for (size_t i = 0; i < SAMPLE_COUNT; ++i) {
            sum += samples[i];
        }
        float mean = static_cast<float>(sum) / SAMPLE_COUNT;

        float variance = 0.0f;
        for (size_t i = 0; i < SAMPLE_COUNT; ++i) {
            float diff = static_cast<float>(samples[i]) - mean;
            variance += diff * diff;
        }
        variance /= SAMPLE_COUNT;

        if (variance > max_variance) {
            return false;
        }

        raw_zero_ = static_cast<uint16_t>(round(mean));
        scale_neg_ = 1.0f / static_cast<float>(raw_zero_ - raw_min_);
        scale_pos_ = 1.0f / static_cast<float>(raw_max_ - raw_zero_);
        calibrated_ = true;
        return true;
    }

    float normalize(uint16_t raw_val) const {
        if (!calibrated_) return 0.0f;
        if (raw_val < raw_zero_) {
            float norm = static_cast<float>(raw_val - raw_zero_) * scale_neg_;
            return (norm < -1.0f) ? -1.0f : norm;
        } else {
            float norm = static_cast<float>(raw_val - raw_zero_) * scale_pos_;
            return (norm > 1.0f) ? 1.0f : norm;
        }
    }
};
