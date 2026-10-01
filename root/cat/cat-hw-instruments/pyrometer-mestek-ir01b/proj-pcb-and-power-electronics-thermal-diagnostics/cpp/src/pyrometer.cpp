#include "pyrometer.hpp"
#include <cmath>
#include <algorithm>

namespace pyrometer {

PyrometerSensor::PyrometerSensor(double sensitivityCoeff)
    : sensitivityCoeff_(sensitivityCoeff) {
    if (sensitivityCoeff_ <= 0.0) {
        sensitivityCoeff_ = 1.2e-11;
    }
}

bool PyrometerSensor::setEmissivity(double emissivity) {
    if (emissivity < 0.10 || emissivity > 1.00) {
        return false;
    }
    emissivity_ = emissivity;
    return true;
}

double PyrometerSensor::getEmissivity() const noexcept {
    return emissivity_;
}

std::optional<double> PyrometerSensor::calculateTargetTemperature(
    double sensorVoltageVolt, 
    double backgroundTempCelsius) const {
    
    if (sensorVoltageVolt < 0.0) {
        return std::nullopt;
    }

    // Переведення фонової температури у Кельвіни: T_bg_K = T_bg_C + 273.15
    const double backgroundTempKelvin = backgroundTempCelsius + KELVIN_OFFSET;
    if (backgroundTempKelvin <= 0.0) {
        return std::nullopt;
    }

    // Закон Стефана — Больцмана з урахуванням емісивності та фонового випромінювання:
    // V_sensor = k * ε * (T_obj^4 - T_bg^4) => T_obj^4 = T_bg^4 + V_sensor / (k * ε)
    const double denominator = sensitivityCoeff_ * emissivity_;
    if (denominator <= 0.0) {
        return std::nullopt;
    }

    const double bgTempFourth = std::pow(backgroundTempKelvin, 4.0);
    const double targetTempFourth = bgTempFourth + (sensorVoltageVolt / denominator);

    if (targetTempFourth <= 0.0) {
        return std::nullopt;
    }

    const double targetTempKelvin = std::pow(targetTempFourth, 0.25);
    const double targetTempCelsius = targetTempKelvin - KELVIN_OFFSET;

    // Перевірка робочого діапазону пірометра MESTEK IR01B (-50 °C ... +550 °C)
    if (targetTempCelsius < -50.0 || targetTempCelsius > 550.0) {
        return std::nullopt;
    }

    return targetTempCelsius;
}

ThermalToleranceEvaluator::ThermalToleranceEvaluator(double warningMarginCelsius)
    : warningMargin_(warningMarginCelsius) {
    if (warningMargin_ < 0.0) {
        warningMargin_ = 15.0;
    }
}

ThermalEvaluationResult ThermalToleranceEvaluator::evaluate(
    const std::string& componentName,
    double measuredTempCelsius,
    double maxAllowedTempCelsius) const {

    ThermalEvaluationResult result;
    result.componentName = componentName;
    result.measuredTempCelsius = measuredTempCelsius;
    result.maxAllowedTempCelsius = maxAllowedTempCelsius;
    result.thermalMarginCelsius = maxAllowedTempCelsius - measuredTempCelsius;

    if (std::isnan(measuredTempCelsius) || std::isnan(maxAllowedTempCelsius)) {
        result.status = ThermalStatus::InvalidReading;
    } else if (measuredTempCelsius > maxAllowedTempCelsius) {
        result.status = ThermalStatus::CriticalOverheat;
    } else if (result.thermalMarginCelsius <= warningMargin_) {
        result.status = ThermalStatus::Warning;
    } else {
        result.status = ThermalStatus::Safe;
    }

    return result;
}

} // namespace pyrometer
