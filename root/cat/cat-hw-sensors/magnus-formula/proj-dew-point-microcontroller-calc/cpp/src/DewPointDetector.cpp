#include "DewPointDetector.hpp"

DewPointDetector::DewPointDetector(float safety_margin)
    : temp_filter_(0.2f), hum_filter_(0.1f), engine_(), // Вологість зазвичай більш "шумна", тому alpha менший
      safety_margin_(safety_margin), last_dew_point_(0.0f),
      filtered_temp_(0.0f), filtered_hum_(0.0f), heater_on_(false) {}

bool DewPointDetector::processReading(float raw_temperature, float raw_humidity) {
    // 1. Очищення даних від шумів
    filtered_temp_ = temp_filter_.update(raw_temperature);
    filtered_hum_ = hum_filter_.update(raw_humidity);

    // 2. Математичний розрахунок точки роси
    last_dew_point_ = engine_.calculateDewPoint(filtered_temp_, filtered_hum_);

    // 3. Інженерна логіка: гістерезис для керування нагрівачем.
    // Визначаємо поріг небезпеки (точка роси + наш запас міцності)
    const float risk_threshold = last_dew_point_ + safety_margin_;

    if (!heater_on_ && filtered_temp_ <= risk_threshold) {
        // Температура впала надто близько до точки роси — вмикаємо нагрівач
        heater_on_ = true;
    } else if (heater_on_ && filtered_temp_ > risk_threshold + 1.5f) {
        // Температура піднялась до безпечного рівня + гістерезис (1.5°C) — вимикаємо
        heater_on_ = false;
    }

    return heater_on_;
}

float DewPointDetector::getLastDewPoint() const {
    return last_dew_point_;
}

float DewPointDetector::getFilteredTemperature() const {
    return filtered_temp_;
}

float DewPointDetector::getFilteredHumidity() const {
    return filtered_hum_;
}
