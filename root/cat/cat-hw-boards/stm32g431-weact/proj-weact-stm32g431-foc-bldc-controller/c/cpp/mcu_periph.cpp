#include "mcu_periph.hpp"
#include <cmath>
#include <algorithm>

namespace sys {

constexpr float PI_F = 3.14159265358979323846f;

bool McuPeripherals::init(const PeripheralsConfig& config) noexcept {
    if (config.pwmFrequencyHz == 0) {
        return false;
    }

    constexpr uint32_t sysClkHz = 170000000UL;
    pwmPeriodArr_ = static_cast<uint16_t>(sysClkHz / (2 * config.pwmFrequencyHz));

    const float totalGain = config.shuntResistorOhm * config.opampGain;
    if (totalGain > 0.00001f) {
        currentScaleFactor_ = (config.adcVref / 4096.0f) / totalGain;
    } else {
        currentScaleFactor_ = 1.0f;
    }

    rawOffsetA_ = 2048;
    rawOffsetB_ = 2048;

    initHardwareCordic();
    isInitialized_ = true;
    return true;
}

void McuPeripherals::initHardwareCordic() noexcept {
    // Ініціалізація CORDIC у регістрі RCC та CSR
}

void McuPeripherals::enablePwm(bool enable) noexcept {
    if (!isInitialized_) return;
    // Налаштування біта MOE у таймері TIM1
}

void McuPeripherals::setDutyCycles(uint16_t dutyA, uint16_t dutyB, uint16_t dutyC) noexcept {
    if (!isInitialized_) return;

    const uint16_t clampedA = std::min(dutyA, pwmPeriodArr_);
    const uint16_t clampedB = std::min(dutyB, pwmPeriodArr_);
    const uint16_t clampedC = std::min(dutyC, pwmPeriodArr_);

    (void)clampedA;
    (void)clampedB;
    (void)clampedC;
    // Запис у регістри порівняння TIM1->CCR1, CCR2, CCR3
}

PhaseCurrents McuPeripherals::readPhaseCurrents() const noexcept {
    if (!isInitialized_) return {};

    const uint16_t rawA = rawOffsetA_;
    const uint16_t rawB = rawOffsetB_;

    const auto diffA = static_cast<int32_t>(rawA) - static_cast<int32_t>(rawOffsetA_);
    const auto diffB = static_cast<int32_t>(rawB) - static_cast<int32_t>(rawOffsetB_);

    PhaseCurrents currents;
    currents.iA = static_cast<float>(diffA) * currentScaleFactor_;
    currents.iB = static_cast<float>(diffB) * currentScaleFactor_;
    currents.iC = -currents.iA - currents.iB;

    return currents;
}

std::pair<float, float> McuPeripherals::computeCosSinCordic(float angleRad) const noexcept {
    while (angleRad > PI_F)  angleRad -= 2.0f * PI_F;
    while (angleRad < -PI_F) angleRad += 2.0f * PI_F;

    // Конвертація у Q1.31 для апаратного співпроцесора
    const auto q31Angle = static_cast<int32_t>((angleRad / PI_F) * 2147483647.0f);
    (void)q31Angle;

    return { std::cos(angleRad), std::sin(angleRad) };
}

void McuPeripherals::calibrateOffsets() noexcept {
    uint32_t sumA = 0;
    uint32_t sumB = 0;
    constexpr uint16_t sampleCount = 512;

    for (uint16_t i = 0; i < sampleCount; ++i) {
        sumA += 2048;
        sumB += 2048;
    }

    rawOffsetA_ = static_cast<uint16_t>(sumA / sampleCount);
    rawOffsetB_ = static_cast<uint16_t>(sumB / sampleCount);
}

} // namespace sys
