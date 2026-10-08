#include "power_logger.hpp"
#include <cmath>

namespace power_monitor {

PowerLogger::PowerLogger(Ina226Driver& driver)
    : driver_(driver) {}

bool PowerLogger::init(double r_shunt_ohms, double max_expected_current_a) {
    reset_metrics();
    return driver_.begin(r_shunt_ohms, max_expected_current_a);
}

void PowerLogger::reset_metrics() {
    metrics_ = PowerMetrics{};
    first_sample_ = true;
    prev_current_a_ = 0.0;
    prev_power_w_ = 0.0;
}

bool PowerLogger::update(double dt_sec) {
    if (driver_.is_sleeping() || dt_sec <= 0.0) {
        return false;
    }

    double bus_v = 0.0;
    double current_a = 0.0;
    double power_w = 0.0;

    if (!driver_.read_all(bus_v, current_a, power_w)) {
        return false;
    }

    metrics_.bus_voltage_v = bus_v;
    metrics_.current_a = current_a;
    metrics_.power_w = power_w;
    metrics_.is_charging = (current_a >= 0.0);

    if (first_sample_) {
        prev_current_a_ = current_a;
        prev_power_w_ = power_w;
        first_sample_ = false;
        metrics_.total_time_sec += dt_sec;
        return true;
    }

    // Дискретне чисельне інтегрування за методом трапецій
    double dt_hours = dt_sec / 3600.0;
    double avg_current = 0.5 * (prev_current_a_ + current_a);
    double avg_power = 0.5 * (prev_power_w_ + power_w);

    double delta_ah = avg_current * dt_hours;
    double delta_wh = avg_power * dt_hours;

    // Роздільний двонапрямлений облік для аналізу процесів заряду й розряду
    if (avg_current >= 0.0) {
        // Режим заряду джерела живлення
        metrics_.charge_ah += delta_ah;
        metrics_.charge_wh += delta_wh;
    } else {
        // Режим розряду джерела живлення
        metrics_.discharge_ah += std::abs(delta_ah);
        metrics_.discharge_wh += delta_wh;
    }

    // Підсумкові чисті значення балансу
    metrics_.net_ah += delta_ah;
    metrics_.net_wh = metrics_.charge_wh - metrics_.discharge_wh;

    metrics_.total_time_sec += dt_sec;

    prev_current_a_ = current_a;
    prev_power_w_ = power_w;

    return true;
}

bool PowerLogger::enter_sleep() {
    return driver_.set_sleep_mode(true);
}

bool PowerLogger::wake_up() {
    bool ok = driver_.set_sleep_mode(false);
    if (ok) {
        // Скидаємо прапорець для запобігання хибному стрибку інтегрування після сну
        first_sample_ = true;
    }
    return ok;
}

} // namespace power_monitor
