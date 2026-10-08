#include <cstdint>
#include <algorithm>

class ServoQuantizer {
public:
    ServoQuantizer(float min_deg, float max_deg, uint32_t min_us, uint32_t max_us, float tick_us)
        : min_deg_(min_deg), max_deg_(max_deg), min_us_(min_us), max_us_(max_us), tick_us_(tick_us) {}

    uint16_t to_ccr(float angle_deg) const {
        float clamped_deg = std::clamp(angle_deg, min_deg_, max_deg_);
        float pulse_us = static_cast<float>(min_us_) + (clamped_deg - min_deg_) * 
                         static_cast<float>(max_us_ - min_us_) / (max_deg_ - min_deg_);
        return static_cast<uint16_t>(pulse_us / tick_us_ + 0.5f);
    }

private:
    float min_deg_;
    float max_deg_;
    uint32_t min_us_;
    uint32_t max_us_;
    float tick_us_;
};
