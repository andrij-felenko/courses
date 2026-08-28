#include <algorithm>
#include <cmath>

namespace drivers {

Hlw8012Driver::Hlw8012Driver(const Hlw8012Config& config) noexcept
    : config_(config) {}

void Hlw8012Driver::on_cf_pulse(uint32_t timestamp_us) noexcept {
    if (last_cf_time_ > 0 && timestamp_us > last_cf_time_) {
        cf_period_us_ = timestamp_us - last_cf_time_;
    }
    last_cf_time_ = timestamp_us;
}

void Hlw8012Driver::on_cf1_pulse(uint32_t timestamp_us) noexcept {
    if (last_cf1_time_ > 0 && timestamp_us > last_cf1_time_) {
        uint32_t period = timestamp_us - last_cf1_time_;
        if (is_voltage_mode_) {
            cf1_v_period_us_ = period;
        } else {
            cf1_i_period_us_ = period;
        }
    }
    last_cf1_time_ = timestamp_us;
}

void Hlw8012Driver::set_sel_state(bool is_voltage_mode) noexcept {
    is_voltage_mode_ = is_voltage_mode;
    last_cf1_time_ = 0; // Скидаємо відлік часу для ігнорування перехідного процесу
}

Hlw8012Readings Hlw8012Driver::get_readings(uint32_t current_time_us) noexcept {
    Hlw8012Readings r;

    // Перевірка таймауту відсутності імпульсів потужності (навантаження вимкнено)
    if (cf_period_us_ > 0 && (current_time_us - last_cf_time_ < config_.pulse_timeout_us)) {
        double freq_cf = 1000000.0 / static_cast<double>(cf_period_us_);
        double calculated_power = freq_cf * config_.k_p;
        
        if (calculated_power >= config_.min_power_w) {
            r.active_power = calculated_power;
        } else {
            r.active_power = 0.0;
        }
    } else {
        r.active_power = 0.0;
    }

    // Обчислення RMS напруги
    if (cf1_v_period_us_ > 0) {
        double freq_v = 1000000.0 / static_cast<double>(cf1_v_period_us_);
        r.v_rms = freq_v * config_.k_v;
    }

    // Обчислення RMS струму
    if (cf1_i_period_us_ > 0) {
        double freq_i = 1000000.0 / static_cast<double>(cf1_i_period_us_);
        r.i_rms = freq_i * config_.k_i;
    }

    // Розрахунок повної потужності S та коефіцієнта потужності PF
    r.apparent_power = r.v_rms * r.i_rms;
    if (r.apparent_power > 1e-3) {
        r.power_factor = std::clamp(r.active_power / r.apparent_power, 0.0, 1.0);
    } else {
        r.power_factor = 1.0;
    }

    return r;
}

} // namespace drivers
