#include "RvdtSensor.hpp"
#include <cmath>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

RvdtSensor::RvdtSensor(const RvdtConfig& config)
    : m_config(config) {
    if (m_config.filterAlpha <= 0.0f || m_config.filterAlpha > 1.0f) {
        m_config.filterAlpha = 0.5f;
    }
}

RvdtStatus RvdtSensor::processAmplitudes(float rawV1Volts, float rawV2Volts) noexcept {
    const float alpha = m_config.filterAlpha;

    // 1. Цифрова фільтрація первинних амплітуд вторинних обмоток (EMA-фільтр)
    if (m_reading.v1Volts == 0.0f && m_reading.v2Volts == 0.0f) {
        m_reading.v1Volts = rawV1Volts;
        m_reading.v2Volts = rawV2Volts;
    } else {
        m_reading.v1Volts = alpha * rawV1Volts + (1.0f - alpha) * m_reading.v1Volts;
        m_reading.v2Volts = alpha * rawV2Volts + (1.0f - alpha) * m_reading.v2Volts;
    }

    const float v1 = m_reading.v1Volts;
    const float v2 = m_reading.v2Volts;
    const float vSum = v1 + v2;

    // 2. Апаратна діагностика стану обмоток
    if (vSum < m_config.vSumMinVolts) {
        m_reading.status = RvdtStatus::WindingOpenCircuit;
        return m_reading.status;
    }

    if (vSum > m_config.vSumMaxVolts) {
        m_reading.status = RvdtStatus::WindingShortCircuit;
        return m_reading.status;
    }

    // 3. Обчислення інваріантного ratiometric-відношення: R = (V1 - V2) / (V1 + V2)
    const float ratio = (v1 - v2) / vSum;
    m_reading.ratiometricRatio = ratio;

    // 4. Розрахунок лінеаризованого кута у градусах
    const float angle = (ratio * m_config.sensitivity) + m_config.zeroOffsetDeg;
    m_reading.angleDegrees = angle;

    // 5. Контроль виходу кута за безпечний діапазон
    if (angle < m_config.minAngleDeg || angle > m_config.maxAngleDeg) {
        m_reading.status = RvdtStatus::SumOutOfRange;
        return m_reading.status;
    }

    m_reading.status = RvdtStatus::Ok;
    return RvdtStatus::Ok;
}

RvdtStatus RvdtSensor::processAdcSamples(std::span<const int16_t> s1Samples,
                                          std::span<const int16_t> s2Samples,
                                          std::span<const int16_t> refSamples,
                                          float vRefVolts,
                                          uint8_t adcBits) noexcept {
    if (s1Samples.empty() || s1Samples.size() != s2Samples.size() || s1Samples.size() != refSamples.size()) {
        m_reading.status = RvdtStatus::InvalidParameters;
        return m_reading.status;
    }

    const float maxAdcCode = static_cast<float>((1U << adcBits) - 1U);
    const float voltsPerLsb = vRefVolts / maxAdcCode;

    float accumS1 = 0.0f;
    float accumS2 = 0.0f;

    // Програмна фазочутлива демодуляція (PSD) за допомогою синхронного перемножувального детектора
    for (size_t i = 0; i < s1Samples.size(); ++i) {
        const float signRef = (refSamples[i] >= 0) ? 1.0f : -1.0f;
        accumS1 += (static_cast<float>(s1Samples[i]) * voltsPerLsb) * signRef;
        accumS2 += (static_cast<float>(s2Samples[i]) * voltsPerLsb) * signRef;
    }

    const float normFactor = static_cast<float>(M_PI) / (2.0f * static_cast<float>(s1Samples.size()));
    const float rawV1 = std::abs(accumS1) * normFactor;
    const float rawV2 = std::abs(accumS2) * normFactor;

    return processAmplitudes(rawV1, rawV2);
}

bool RvdtSensor::calibrateZero() noexcept {
    m_config.zeroOffsetDeg -= m_reading.angleDegrees;
    m_reading.angleDegrees = 0.0f;
    return true;
}

bool RvdtSensor::calibrateSpan(float referenceAngleDeg) noexcept {
    if (std::abs(m_reading.ratiometricRatio) < 1e-5f) {
        return false;
    }
    const float uncompensated = referenceAngleDeg - m_config.zeroOffsetDeg;
    m_config.sensitivity = uncompensated / m_reading.ratiometricRatio;
    m_reading.angleDegrees = referenceAngleDeg;
    return true;
}

std::string_view RvdtSensor::statusToString(RvdtStatus status) noexcept {
    switch (status) {
        case RvdtStatus::Ok:                  return "ОК (Норма)";
        case RvdtStatus::WindingOpenCircuit:  return "АВАРІЯ: Обрив обмотки / втрата збудження";
        case RvdtStatus::WindingShortCircuit: return "АВАРІЯ: Коротке замикання обмотки";
        case RvdtStatus::SumOutOfRange:       return "ПОПЕРЕДЖЕННЯ: Кут поза діапазоном";
        case RvdtStatus::InvalidParameters:   return "ПОМИЛКА: Некоректні параметри АЦП";
    }
    return "НЕВІДОМИЙ СТАН";
}
