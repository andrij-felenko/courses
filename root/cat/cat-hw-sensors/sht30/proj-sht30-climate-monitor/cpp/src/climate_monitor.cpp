#include "climate_monitor.hpp"
#include <cmath>
#include <thread>
#include <algorithm>

namespace sensors {

ClimateMonitor::ClimateMonitor(SHT30& sensor, float condensation_threshold_rh)
    : sensor_(sensor), condensation_threshold_rh_(condensation_threshold_rh) {}

float ClimateMonitor::calculate_dew_point(float temp_c, float rh_percent) noexcept {
    // Запобігаємо логарифмуванню нуля або від'ємних значень
    const float rh = std::clamp(rh_percent, 0.1f, 100.0f);

    // Коефіцієнти формули Магнуса для вузького діапазону температур (-45°C..+60°C)
    const float a = 17.625f;
    const float b = 243.04f;

    const float alpha = ((a * temp_c) / (b + temp_c)) + std::log(rh / 100.0f);
    return (b * alpha) / (a - alpha);
}

ClimateStatus ClimateMonitor::update() {
    ClimateStatus status{};

    Sht30Data raw_data = sensor_.read_measurement(SHT30::Repeatability::High);
    if (!raw_data.is_valid) {
        status.crc_ok = false;
        return status;
    }

    status.crc_ok = true;
    status.temperature_c = raw_data.temperature_c;
    status.humidity_percent = raw_data.humidity_percent;
    status.dew_point_c = calculate_dew_point(status.temperature_c, status.humidity_percent);

    // Ризик конденсації виникає при дуже високій вологості або наближенні T до точки роси
    const bool high_humidity = (status.humidity_percent >= condensation_threshold_rh_);
    const bool near_dew_point = ((status.temperature_c - status.dew_point_c) <= 2.0f);
    status.condensation_risk = high_humidity || near_dew_point;

    return status;
}

bool ClimateMonitor::perform_decondensation_cycle(std::chrono::milliseconds duration) {
    // 1. Вмикаємо нагрівач SHT30 для випаровування води з поверхні елемента
    if (!sensor_.set_heater(true)) {
        return false;
    }

    // 2. Утримуємо нагрівач увімкненим заданий час
    std::this_thread::sleep_for(duration);

    // 3. Вимикаємо нагрівач
    bool ok = sensor_.set_heater(false);

    // 4. Виконуємо програмне скидання для стабілізації стану
    ok = ok && sensor_.soft_reset();
    return ok;
}

bool ClimateMonitor::enter_sleep_mode() {
    return sensor_.sleep();
}

} // namespace sensors
