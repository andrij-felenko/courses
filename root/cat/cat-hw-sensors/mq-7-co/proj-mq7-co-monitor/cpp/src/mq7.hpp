#pragma once

#include <cstdint>
#include <functional>

namespace mq7 {

enum class HeatingState {
    HighVoltage, // 60s нагрів
    LowVoltage,  // 90s охолодження
    Reading      // зчитування після охолодження
};

struct Config {
    float r0_baseline;
    float threshold_ppm;
    uint32_t high_duration_ms = 60000;
    uint32_t low_duration_ms = 90000;
};

class MQ7 {
public:
    using HardwareTimeMsFn = std::function<uint32_t()>;
    using HardwareAnalogReadFn = std::function<uint16_t()>;
    using HardwareHeaterPwmFn = std::function<void(uint8_t)>;
    using AlarmCallback = std::function<void(float ppm)>;

    MQ7(Config config, 
        HardwareTimeMsFn time_fn, 
        HardwareAnalogReadFn read_fn, 
        HardwareHeaterPwmFn pwm_fn,
        AlarmCallback alarm_cb);

    void update();
    float get_ppm() const;
    HeatingState get_state() const;

private:
    float calculate_ppm(uint16_t analog_value);
    
    Config config_;
    HardwareTimeMsFn get_time_ms_;
    HardwareAnalogReadFn analog_read_;
    HardwareHeaterPwmFn set_heater_;
    AlarmCallback on_alarm_;

    HeatingState current_state_;
    uint32_t state_start_time_;
    float current_ppm_;
};

} // namespace mq7
