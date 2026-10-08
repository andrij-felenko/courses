#include "servo_feedback.hpp"
#include <algorithm>

ServoFeedback::ServoFeedback(const CalibrationParams& calib, float filter_alpha)
    : calib_(calib), filter_(filter_alpha) {
    if (!calib_.is_valid()) {
        status_ = SensorStatus::InvalidConfig;
    }
}

bool ServoFeedback::set_calibration(const CalibrationParams& calib) noexcept {
    if (!calib.is_valid()) {
        status_ = SensorStatus::InvalidConfig;
        return false;
    }
    calib_ = calib;
    if (status_ == SensorStatus::InvalidConfig) {
        status_ = SensorStatus::Ok;
    }
    return true;
}

const CalibrationParams& ServoFeedback::calibration() const noexcept {
    return calib_;
}

SensorStatus ServoFeedback::update_raw(uint16_t raw_adc) noexcept {
    last_raw_ = raw_adc;

    // Перевірка ліквідності конфігурації
    if (!calib_.is_valid()) {
        status_ = SensorStatus::InvalidConfig;
        return status_;
    }

    // Перевірка допустимих меж відліку АЦП
    if (raw_adc < calib_.raw_min) {
        status_ = SensorStatus::Underflow;
    } else if (raw_adc > calib_.raw_max) {
        status_ = SensorStatus::Overflow;
    } else {
        status_ = SensorStatus::Ok;
    }

    // Згладжування сирих даних за допомогою EMA-фільтра
    filter_.update(static_cast<float>(raw_adc));

    return status_;
}

float ServoFeedback::angle_degrees() const noexcept {
    if (!calib_.is_valid()) {
        return 0.0f;
    }

    // Використовуємо відфільтроване значення для обчислення кута
    return raw_to_degrees(filter_.value());
}

float ServoFeedback::filtered_raw() const noexcept {
    return filter_.value();
}

uint16_t ServoFeedback::raw_adc() const noexcept {
    return last_raw_;
}

SensorStatus ServoFeedback::status() const noexcept {
    return status_;
}

void ServoFeedback::reset_filter() noexcept {
    filter_.reset();
}

bool ServoFeedback::is_in_range(uint16_t raw_adc, const CalibrationParams& calib) noexcept {
    return (raw_adc >= calib.raw_min) && (raw_adc <= calib.raw_max);
}

float ServoFeedback::raw_to_degrees(float raw_val) const noexcept {
    // Враховуємо зміщення нуля
    float adjusted_raw = raw_val - static_cast<float>(calib_.raw_zero_offset);

    // Обмеження adjusted_raw діапазоном [raw_min, raw_max] для відсікання екстремальних викидів
    float min_r = static_cast<float>(calib_.raw_min);
    float max_r = static_cast<float>(calib_.raw_max);
    float clamped_raw = std::clamp(adjusted_raw, min_r, max_r);

    // Нормалізація у діапазон [0.0, 1.0]
    float normalized = (clamped_raw - min_r) / (max_r - min_r);

    // Масштабування у діапазон кутів [min_angle_deg, max_angle_deg]
    return calib_.min_angle_deg + normalized * (calib_.max_angle_deg - calib_.min_angle_deg);
}
