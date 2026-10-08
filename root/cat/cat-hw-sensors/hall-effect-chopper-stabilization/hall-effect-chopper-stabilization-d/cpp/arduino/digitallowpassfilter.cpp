#include <Arduino.h>

class DigitalLowPassFilter {
private:
    float alpha_;
    float prev_output_;

public:
    DigitalLowPassFilter(float cutoff_hz, float sample_rate_hz) {
        float dt = 1.0f / sample_rate_hz;
        float omega = 2.0f * 3.14159265f * cutoff_hz;
        alpha_ = (omega * dt) / (1.0f + omega * dt);
        prev_output_ = 0.0f;
    }

    float process(float raw_adc_volts) {
        float filtered = alpha_ * raw_adc_volts + (1.0f - alpha_) * prev_output_;
        prev_output_ = filtered;
        return filtered;
    }
};
