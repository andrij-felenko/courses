#include "mq7.hpp"
#include <cmath>

namespace mq7 {

// Константні коефіцієнти для MQ-7 з даташиту
// Rs/R0 = A * (PPM)^B
constexpr float A = 99.042f;
constexpr float B = -1.518f;

MQ7::MQ7(Config config, 
         HardwareTimeMsFn time_fn, 
         HardwareAnalogReadFn read_fn, 
         HardwareHeaterPwmFn pwm_fn,
         AlarmCallback alarm_cb)
    : config_(config),
      get_time_ms_(time_fn),
      analog_read_(read_fn),
      set_heater_(pwm_fn),
      on_alarm_(alarm_cb),
      current_state_(HeatingState::HighVoltage),
      state_start_time_(time_fn()),
      current_ppm_(0.0f) 
{
    // 100% ШІМ зазвичай відповідає 5V
    set_heater_(255); 
}

void MQ7::update() {
    uint32_t current_time = get_time_ms_();
    uint32_t elapsed = current_time - state_start_time_;

    switch (current_state_) {
        case HeatingState::HighVoltage:
            if (elapsed >= config_.high_duration_ms) {
                current_state_ = HeatingState::LowVoltage;
                state_start_time_ = current_time;
                // Встановлюємо ~1.4V для охолодження (255 * 1.4 / 5.0 ≈ 71)
                set_heater_(71);
            }
            break;

        case HeatingState::LowVoltage:
            if (elapsed >= config_.low_duration_ms) {
                current_state_ = HeatingState::Reading;
                state_start_time_ = current_time;
            }
            break;

        case HeatingState::Reading: {
            uint16_t raw_val = analog_read_();
            current_ppm_ = calculate_ppm(raw_val);
            
            if (current_ppm_ > config_.threshold_ppm && on_alarm_) {
                on_alarm_(current_ppm_);
            }

            // Повертаємось до нагрівання
            current_state_ = HeatingState::HighVoltage;
            state_start_time_ = current_time;
            set_heater_(255);
            break;
        }
    }
}

float MQ7::get_ppm() const {
    return current_ppm_;
}

HeatingState MQ7::get_state() const {
    return current_state_;
}

float MQ7::calculate_ppm(uint16_t analog_value) {
    // Припускаємо 10-бітне АЦП (0-1023)
    if (analog_value == 0) return 0.0f;
    
    // Перетворення значення АЦП у напругу (припускаємо 5V живлення)
    float sensor_voltage = (analog_value / 1023.0f) * 5.0f;
    
    // Опір навантаження (резистор на платі модуля) R_L зазвичай 10 кОм
    constexpr float R_LOAD = 10.0f; 
    
    // Обчислення опору сенсора Rs
    float rs = ((5.0f * R_LOAD) / sensor_voltage) - R_LOAD;
    
    // Відношення Rs/R0
    float ratio = rs / config_.r0_baseline;
    
    // Обчислення PPM: PPM = (Rs/R0 / A)^(1/B)
    return std::pow(ratio / A, 1.0f / B);
}

} // namespace mq7
