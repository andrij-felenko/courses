#include "Pt100Normalizer.hpp"
#include <cmath>

Pt100Normalizer::Pt100Normalizer(uint32_t max_adc_count,
                                 float vref_volts,
                                 float min_expected_voltage,
                                 float max_expected_voltage)
    : max_adc_count_(max_adc_count > 0 ? max_adc_count : 4095),
      vref_volts_(vref_volts > 0.0f ? vref_volts : 3.3f),
      min_expected_voltage_(min_expected_voltage),
      max_expected_voltage_(max_expected_voltage)
{
    // За замовчуванням встановлюємо номінальний діапазон 0...100 °C для напруги 0...Vref
    setNominalRange(0.0f, 100.0f);
}

float Pt100Normalizer::rawToVoltage(uint32_t raw_adc) const noexcept {
    if (raw_adc > max_adc_count_) {
        return vref_volts_;
    }
    return (static_cast<float>(raw_adc) / static_cast<float>(max_adc_count_)) * vref_volts_;
}

void Pt100Normalizer::setNominalRange(float temp_min, float temp_max) noexcept {
    // Розрахунок номінального нахилу: gain = (T_max - T_min) / N_max
    if (max_adc_count_ > 0 && std::abs(temp_max - temp_min) > 1e-4f) {
        coeffs_.gain = (temp_max - temp_min) / static_cast<float>(max_adc_count_);
        coeffs_.offset = temp_min;
        is_calibrated_ = false;
    }
}

bool Pt100Normalizer::calibrate(const CalibPoint& p1, const CalibPoint& p2) noexcept {
    // Перевірка допустимості відліків АЦП
    if (p1.raw_adc > max_adc_count_ || p2.raw_adc > max_adc_count_) {
        return false;
    }

    // Перевірка відсутності збігу відліків та температур (запобігання діленню на нуль)
    const float raw_diff = static_cast<float>(p2.raw_adc) - static_cast<float>(p1.raw_adc);
    const float temp_diff = p2.reference_temp - p1.reference_temp;

    if (std::abs(raw_diff) < 1.0f || std::abs(temp_diff) < 1e-3f) {
        return false;
    }

    // Математична модель двохточкового калібрування:
    // gain = (T2 - T1) / (ADC2 - ADC1)
    // offset = T1 - gain * ADC1
    const float calculated_gain = temp_diff / raw_diff;
    const float calculated_offset = p1.reference_temp - calculated_gain * static_cast<float>(p1.raw_adc);

    coeffs_.gain = calculated_gain;
    coeffs_.offset = calculated_offset;
    is_calibrated_ = true;

    return true;
}

bool Pt100Normalizer::setCoefficients(const CalibCoeffs& coeffs) noexcept {
    if (std::isnan(coeffs.gain) || std::isnan(coeffs.offset) || std::abs(coeffs.gain) < 1e-9f) {
        return false;
    }
    coeffs_ = coeffs;
    is_calibrated_ = true;
    return true;
}

CalibCoeffs Pt100Normalizer::getCoefficients() const noexcept {
    return coeffs_;
}

SensorStatus Pt100Normalizer::checkSignalIntegrity(uint32_t raw_adc) const noexcept {
    if (raw_adc > max_adc_count_) {
        return SensorStatus::AdcOutOfRange;
    }

    const float voltage = rawToVoltage(raw_adc);

    if (voltage < min_expected_voltage_) {
        return SensorStatus::ShortCircuit;
    }
    if (voltage > max_expected_voltage_) {
        return SensorStatus::OpenCircuit;
    }

    return is_calibrated_ ? SensorStatus::Ok : SensorStatus::Uncalibrated;
}

std::optional<float> Pt100Normalizer::readTemperature(uint32_t raw_adc, SensorStatus& out_status) const noexcept {
    out_status = checkSignalIntegrity(raw_adc);

    // У разі апаратної аварії лінії вимірювання повертаємо порожнє значення
    if (out_status == SensorStatus::AdcOutOfRange ||
        out_status == SensorStatus::ShortCircuit ||
        out_status == SensorStatus::OpenCircuit) {
        return std::nullopt;
    }

    // Лінійне перетворення: T = gain * raw_adc + offset
    const float temp = coeffs_.gain * static_cast<float>(raw_adc) + coeffs_.offset;

    // Перевірка відповідності розрахованої температури фізичному діапазону PT100 (-200 °C ... +850 °C)
    constexpr float kMinPt100Temp = -200.0f;
    constexpr float kMaxPt100Temp = 850.0f;

    if (temp < kMinPt100Temp || temp > kMaxPt100Temp) {
        out_status = SensorStatus::TemperatureOutOfRange;
        return std::nullopt;
    }

    return temp;
}

float Pt100Normalizer::rawToTemperature(uint32_t raw_adc) const noexcept {
    SensorStatus status{};
    const auto result = readTemperature(raw_adc, status);
    return result.has_value() ? result.value() : static_cast<float>(NAN);
}
