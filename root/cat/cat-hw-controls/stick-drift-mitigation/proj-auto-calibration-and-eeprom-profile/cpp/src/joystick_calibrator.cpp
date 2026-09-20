#include "joystick_calibrator.hpp"
#include <cmath>
#include <algorithm>
#include <numeric>

JoystickCalibrator::JoystickCalibrator(const CalibrationProfile& profile) {
    if (validateProfile(profile)) {
        profile_ = profile;
    } else {
        profile_ = createDefaultProfile();
    }
}

uint16_t JoystickCalibrator::calculateCRC16(const uint8_t* data, size_t length) {
    // Алгоритм CRC16-CCITT (прямий розрахунок, поліном 0x1021, початкове значення 0xFFFF)
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < length; ++i) {
        crc ^= static_cast<uint16_t>(data[i]) << 8;
        for (uint8_t bit = 0; bit < 8; ++bit) {
            if (crc & 0x8000) {
                crc = (crc << 1) ^ 0x1021;
            } else {
                crc <<= 1;
            }
        }
    }
    return crc;
}

uint16_t JoystickCalibrator::calculateProfileCRC(const CalibrationProfile& profile) {
    // Хешуємо всі байтові поля структури до зміщення поля crc
    const size_t bytesToHash = offsetof(CalibrationProfile, crc);
    const auto* dataPtr = reinterpret_cast<const uint8_t*>(&profile);
    return calculateCRC16(dataPtr, bytesToHash);
}

bool JoystickCalibrator::validateProfile(const CalibrationProfile& profile) {
    // Перевірка відповідності збереженого значення CRC розрахованому
    if (profile.crc != calculateProfileCRC(profile)) {
        return false;
    }

    // Санітарні перевірки коректності геометричних меж профілю
    if (profile.minX >= profile.maxX || profile.minY >= profile.maxY) {
        return false;
    }
    if (profile.centerX <= profile.minX || profile.centerX >= profile.maxX) {
        return false;
    }
    if (profile.centerY <= profile.minY || profile.centerY >= profile.maxY) {
        return false;
    }
    if (profile.deadbandRadius < 0.0f || profile.deadbandRadius >= 0.5f) {
        return false;
    }

    return true;
}

CalibrationProfile JoystickCalibrator::createDefaultProfile() {
    CalibrationProfile profile;
    profile.minX = 0;
    profile.maxX = 4095;
    profile.centerX = 2048;
    profile.minY = 0;
    profile.maxY = 4095;
    profile.centerY = 2048;
    profile.deadbandRadius = 0.08f;
    profile.crc = calculateProfileCRC(profile);
    return profile;
}

void JoystickCalibrator::autoCalibrateNeutral(const std::vector<int16_t>& rawSamplesX,
                                              const std::vector<int16_t>& rawSamplesY) {
    if (rawSamplesX.empty() || rawSamplesY.empty()) {
        return;
    }

    // Обчислення середнього значення АЦП для точно визначеного центрального положення
    const int64_t sumX = std::accumulate(rawSamplesX.begin(), rawSamplesX.end(), int64_t{0});
    const int64_t sumY = std::accumulate(rawSamplesY.begin(), rawSamplesY.end(), int64_t{0});

    profile_.centerX = static_cast<int16_t>(sumX / static_cast<int64_t>(rawSamplesX.size()));
    profile_.centerY = static_cast<int16_t>(sumY / static_cast<int64_t>(rawSamplesY.size()));

    // Захисна обрізка значення центру в межах встановленого діапазону
    profile_.centerX = std::clamp(profile_.centerX, profile_.minX, profile_.maxX);
    profile_.centerY = std::clamp(profile_.centerY, profile_.minY, profile_.maxY);

    updateCRC();
}

void JoystickCalibrator::updateLimits(int16_t rawX, int16_t rawY) {
    // Фіксація екстремальних відхилень важеля джойстика
    profile_.minX = std::min(profile_.minX, rawX);
    profile_.maxX = std::max(profile_.maxX, rawX);
    profile_.minY = std::min(profile_.minY, rawY);
    profile_.maxY = std::max(profile_.maxY, rawY);

    updateCRC();
}

NormalizedOutput JoystickCalibrator::processRawInput(int16_t rawX, int16_t rawY) const {
    // 1. Асиметричне лінійне масштабування осей відносно виміряного центру
    float normX = 0.0f;
    float normY = 0.0f;

    const int32_t dx = static_cast<int32_t>(rawX) - profile_.centerX;
    if (dx >= 0) {
        const int32_t spanX = static_cast<int32_t>(profile_.maxX) - profile_.centerX;
        normX = (spanX > 0) ? static_cast<float>(dx) / static_cast<float>(spanX) : 0.0f;
    } else {
        const int32_t spanX = static_cast<int32_t>(profile_.centerX) - profile_.minX;
        normX = (spanX > 0) ? static_cast<float>(dx) / static_cast<float>(spanX) : 0.0f;
    }

    const int32_t dy = static_cast<int32_t>(rawY) - profile_.centerY;
    if (dy >= 0) {
        const int32_t spanY = static_cast<int32_t>(profile_.maxY) - profile_.centerY;
        normY = (spanY > 0) ? static_cast<float>(dy) / static_cast<float>(spanY) : 0.0f;
    } else {
        const int32_t spanY = static_cast<int32_t>(profile_.centerY) - profile_.minY;
        normY = (spanY > 0) ? static_cast<float>(dy) / static_cast<float>(spanY) : 0.0f;
    }

    normX = std::clamp(normX, -1.0f, 1.0f);
    normY = std::clamp(normY, -1.0f, 1.0f);

    // 2. Обчислення радіальної мертвої зони (Deadband) для плавного зрізання шуму дрейфу
    const float radius = std::sqrt(normX * normX + normY * normY);

    NormalizedOutput output;
    if (radius <= profile_.deadbandRadius || radius < 1e-6f) {
        output.x = 0.0f;
        output.y = 0.0f;
    } else {
        // Рескалювання від межі мертвої зони до 1.0 для плавного керування
        const float scaledRadius = std::min(1.0f, (radius - profile_.deadbandRadius) / (1.0f - profile_.deadbandRadius));
        const float scaleFactor = scaledRadius / radius;
        output.x = std::clamp(normX * scaleFactor, -1.0f, 1.0f);
        output.y = std::clamp(normY * scaleFactor, -1.0f, 1.0f);
    }

    return output;
}

void JoystickCalibrator::setProfile(const CalibrationProfile& profile) {
    profile_ = profile;
    updateCRC();
}

void JoystickCalibrator::updateCRC() {
    profile_.crc = calculateProfileCRC(profile_);
}
