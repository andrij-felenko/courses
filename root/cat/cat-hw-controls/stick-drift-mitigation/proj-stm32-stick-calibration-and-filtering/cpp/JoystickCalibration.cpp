#include "JoystickCalibration.h"
#include <cmath>
#include <algorithm>

JoystickCalibration::JoystickCalibration() {
    updateConfigCRC(config_);
}

JoystickError JoystickCalibration::begin(const JoystickConfig& config) {
    if (!validateConfig(config)) {
        return JoystickError::CRC_MISMATCH;
    }

    if (config.min_x >= config.max_x || config.min_y >= config.max_y ||
        config.center_x <= config.min_x || config.center_x >= config.max_x ||
        config.center_y <= config.min_y || config.center_y >= config.max_y) {
        return JoystickError::INVALID_RANGE;
    }

    config_ = config;
    return JoystickError::OK;
}

NormalizedPoint JoystickCalibration::process(int16_t raw_x, int16_t raw_y) {
    // Якщо триває неблокуюче калібрування — оновлюємо накопичувачі
    if (calibrating_neutral_) {
        updateNeutralCalibration(raw_x, raw_y);
    }
    if (calibrating_range_) {
        updateRangeCalibration(raw_x, raw_y);
    }

    // 1. Асиметричне масштабування півдіапазонів АЦП у координати [-1.0 .. +1.0]
    float norm_x = normalizeAxis(raw_x, config_.center_x, config_.min_x, config_.max_x);
    float norm_y = normalizeAxis(raw_y, config_.center_y, config_.min_y, config_.max_y);

    float out_x = norm_x;
    float out_y = norm_y;

    // 2. Фільтрація мертвих зон
    if (config_.deadzone_type == static_cast<uint8_t>(DeadzoneType::ScaledRadial)) {
        applyScaledRadialDeadzone(norm_x, norm_y, config_.deadzone_radial, out_x, out_y);
    } else {
        applyAxialDeadzone(norm_x, norm_y, config_.deadzone_axial, out_x, out_y);
    }

    return NormalizedPoint{out_x, out_y};
}

float JoystickCalibration::normalizeAxis(int16_t raw_val, int16_t center, int16_t min_val, int16_t max_val) const {
    if (raw_val >= center) {
        int16_t span = max_val - center;
        if (span <= 0) return 0.0f;
        float norm = static_cast<float>(raw_val - center) / static_cast<float>(span);
        return (norm > 1.0f) ? 1.0f : norm;
    } else {
        int16_t span = center - min_val;
        if (span <= 0) return 0.0f;
        float norm = static_cast<float>(raw_val - center) / static_cast<float>(span);
        return (norm < -1.0f) ? -1.0f : norm;
    }
}

void JoystickCalibration::applyScaledRadialDeadzone(float in_x, float in_y, float deadzone, float& out_x, float& out_y) const {
    float magnitude = std::sqrt(in_x * in_x + in_y * in_y);

    if (magnitude <= deadzone || magnitude < 1e-6f) {
        out_x = 0.0f;
        out_y = 0.0f;
        return;
    }

    // Масштабування амплітуди від межі мертвої зони до одиничного диска [0.0 .. 1.0]
    float scaled_magnitude = (magnitude - deadzone) / (1.0f - deadzone);
    if (scaled_magnitude > 1.0f) {
        scaled_magnitude = 1.0f;
    }

    // Збереження вхідного полярного кута (без кутового викривлення)
    out_x = (in_x / magnitude) * scaled_magnitude;
    out_y = (in_y / magnitude) * scaled_magnitude;
}

void JoystickCalibration::applyAxialDeadzone(float in_x, float in_y, float deadzone, float& out_x, float& out_y) const {
    out_x = (std::abs(in_x) < deadzone) ? 0.0f : in_x;
    out_y = (std::abs(in_y) < deadzone) ? 0.0f : in_y;
}

void JoystickCalibration::setDeadzoneRadial(float ratio) {
    if (ratio >= 0.0f && ratio < 0.5f) {
        config_.deadzone_radial = ratio;
        updateConfigCRC(config_);
    }
}

void JoystickCalibration::setDeadzoneAxial(float ratio) {
    if (ratio >= 0.0f && ratio < 0.5f) {
        config_.deadzone_axial = ratio;
        updateConfigCRC(config_);
    }
}

void JoystickCalibration::setDeadzoneType(DeadzoneType type) {
    config_.deadzone_type = static_cast<uint8_t>(type);
    updateConfigCRC(config_);
}

void JoystickCalibration::startNeutralCalibration() {
    sum_x_ = 0;
    sum_y_ = 0;
    sample_count_ = 0;
    calibrating_neutral_ = true;
}

void JoystickCalibration::updateNeutralCalibration(int16_t raw_x, int16_t raw_y) {
    if (!calibrating_neutral_) return;
    sum_x_ += raw_x;
    sum_y_ += raw_y;
    sample_count_++;
}

void JoystickCalibration::finishNeutralCalibration() {
    if (!calibrating_neutral_ || sample_count_ == 0) return;

    config_.center_x = static_cast<int16_t>(sum_x_ / static_cast<int32_t>(sample_count_));
    config_.center_y = static_cast<int16_t>(sum_y_ / static_cast<int32_t>(sample_count_));

    calibrating_neutral_ = false;
    updateConfigCRC(config_);
}

void JoystickCalibration::startRangeCalibration() {
    calib_min_x_ = 32767;
    calib_max_x_ = -32768;
    calib_min_y_ = 32767;
    calib_max_y_ = -32768;
    calibrating_range_ = true;
}

void JoystickCalibration::updateRangeCalibration(int16_t raw_x, int16_t raw_y) {
    if (!calibrating_range_) return;

    if (raw_x < calib_min_x_) calib_min_x_ = raw_x;
    if (raw_x > calib_max_x_) calib_max_x_ = raw_x;
    if (raw_y < calib_min_y_) calib_min_y_ = raw_y;
    if (raw_y > calib_max_y_) calib_max_y_ = raw_y;
}

void JoystickCalibration::finishRangeCalibration() {
    if (!calibrating_range_) return;

    if (calib_min_x_ < calib_max_x_) {
        config_.min_x = calib_min_x_;
        config_.max_x = calib_max_x_;
    }
    if (calib_min_y_ < calib_max_y_) {
        config_.min_y = calib_min_y_;
        config_.max_y = calib_max_y_;
    }

    calibrating_range_ = false;
    updateConfigCRC(config_);
}

uint16_t JoystickCalibration::calculateCRC16(const uint8_t* data, size_t length) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < length; ++i) {
        crc ^= static_cast<uint16_t>(data[i]);
        for (uint8_t bit = 0; bit < 8; ++bit) {
            if (crc & 0x0001) {
                crc = (crc >> 1) ^ 0xA001;
            } else {
                crc >>= 1;
            }
        }
    }
    return crc;
}

bool JoystickCalibration::validateConfig(const JoystickConfig& cfg) const {
    size_t payload_len = offsetof(JoystickConfig, crc16);
    uint16_t computed = calculateCRC16(reinterpret_cast<const uint8_t*>(&cfg), payload_len);
    return (computed == cfg.crc16);
}

void JoystickCalibration::updateConfigCRC(JoystickConfig& cfg) {
    size_t payload_len = offsetof(JoystickConfig, crc16);
    cfg.crc16 = calculateCRC16(reinterpret_cast<const uint8_t*>(&cfg), payload_len);
}
