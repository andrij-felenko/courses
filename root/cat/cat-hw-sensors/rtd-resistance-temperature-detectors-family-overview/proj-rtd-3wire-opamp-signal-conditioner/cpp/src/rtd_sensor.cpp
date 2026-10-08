#include "rtd_sensor.hpp"
#include <cmath>
#include <algorithm>

namespace sensors::rtd {

bool CalibrationParams::calibrateTwoPoint(double r_std1, double r_meas1, double r_std2, double r_meas2) {
    const double delta_meas = r_meas2 - r_meas1;
    if (std::abs(delta_meas) < 1e-9) {
        return false;
    }
    scale_factor = (r_std2 - r_std1) / delta_meas;
    offset_ohms = r_std1 - (scale_factor * r_meas1);
    return true;
}

std::string_view statusToString(SensorStatus status) {
    switch (status) {
        case SensorStatus::Ok:               return "OK";
        case SensorStatus::Underflow:        return "Помилка: Температура нижча за припустиму межу";
        case SensorStatus::Overflow:         return "Помилка: Температура вища за припустиму межу";
        case SensorStatus::OpenCircuit:      return "Аварія: Обрив вимірювального кола (Open Circuit)";
        case SensorStatus::ShortCircuit:     return "Аварія: Коротке замикання датчика (Short Circuit)";
        case SensorStatus::InvalidAdcCode:   return "Помилка: Вихід коду АЦП за межі розрядності";
        case SensorStatus::CalibrationError: return "Помилка: Невалідні коефіцієнти калібрування";
    }
    return "Невідомий статус";
}

RtdSensor::RtdSensor(const AdcConfig& adc_config,
                     RtdType rtd_type,
                     const CalibrationParams& cal_params,
                     double min_temp_c,
                     double max_temp_c)
    : adc_config_(adc_config),
      cal_params_(cal_params),
      solver_(rtd_type),
      min_temp_c_(min_temp_c),
      max_temp_c_(max_temp_c) {
    updateResistanceLimits();
}

void RtdSensor::updateResistanceLimits() {
    const double r_min = solver_.temperatureToResistance(min_temp_c_);
    const double r_max = solver_.temperatureToResistance(max_temp_c_);

    min_resistance_ohms_ = std::max(0.1, r_min * 0.9);
    max_resistance_ohms_ = r_max * 1.1;
}

void RtdSensor::setAdcConfig(const AdcConfig& config) {
    adc_config_ = config;
}

void RtdSensor::setCalibrationParams(const CalibrationParams& params) {
    cal_params_ = params;
}

void RtdSensor::setTemperatureLimits(double min_c, double max_c) {
    min_temp_c_ = min_c;
    max_temp_c_ = max_c;
    updateResistanceLimits();
}

double RtdSensor::adcCodeToVoltage(int32_t adc_code) const {
    const double max_code = adc_config_.getMaxCode();
    if (max_code <= 0.0 || adc_config_.gain <= 0.0) {
        return 0.0;
    }
    const double code_val = static_cast<double>(adc_code);
    return (code_val / max_code) * (adc_config_.vref_volts / adc_config_.gain);
}

double RtdSensor::adcCodeToRawResistance(int32_t adc_code) const {
    const double max_code = adc_config_.getMaxCode();
    if (max_code <= 0.0 || adc_config_.gain <= 0.0) {
        return 0.0;
    }

    const double code_val = static_cast<double>(adc_code);

    if (adc_config_.is_ratiometric) {
        return (code_val * adc_config_.r_ref_ohms) / (max_code * adc_config_.gain);
    } else {
        const double voltage = adcCodeToVoltage(adc_code);
        if (adc_config_.i_bias_amps <= 0.0) {
            return 0.0;
        }
        return voltage / adc_config_.i_bias_amps;
    }
}

bool RtdSensor::calibrateTwoPoint(double r_std1, int32_t adc_code1, double r_std2, int32_t adc_code2) {
    const double r_meas1 = adcCodeToRawResistance(adc_code1);
    const double r_meas2 = adcCodeToRawResistance(adc_code2);
    return cal_params_.calibrateTwoPoint(r_std1, r_meas1, r_std2, r_meas2);
}

MeasurementResult RtdSensor::processAdcCode(int32_t adc_code) const {
    MeasurementResult result;
    const double max_code = adc_config_.getMaxCode();

    if (adc_code < 0 || static_cast<double>(adc_code) > max_code) {
        result.status = SensorStatus::InvalidAdcCode;
        return result;
    }

    result.voltage_volts = adcCodeToVoltage(adc_code);
    result.resistance_raw_ohms = adcCodeToRawResistance(adc_code);

    if (result.resistance_raw_ohms > max_resistance_ohms_) {
        result.status = SensorStatus::OpenCircuit;
        return result;
    }
    if (result.resistance_raw_ohms < min_resistance_ohms_) {
        result.status = SensorStatus::ShortCircuit;
        return result;
    }

    result.resistance_cal_ohms = cal_params_.apply(result.resistance_raw_ohms);

    const auto temp_opt = solver_.resistanceToTemperature(result.resistance_cal_ohms);
    if (!temp_opt.has_value()) {
        result.status = SensorStatus::CalibrationError;
        return result;
    }

    result.temperature_c = temp_opt.value();

    if (result.temperature_c < min_temp_c_) {
        result.status = SensorStatus::Underflow;
    } else if (result.temperature_c > max_temp_c_) {
        result.status = SensorStatus::Overflow;
    } else {
        result.status = SensorStatus::Ok;
    }

    return result;
}

} // namespace sensors::rtd
