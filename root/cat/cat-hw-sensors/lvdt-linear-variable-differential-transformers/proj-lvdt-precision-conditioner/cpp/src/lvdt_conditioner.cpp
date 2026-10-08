#include "lvdt_conditioner.hpp"
#include <cmath>

namespace lvdt {

LVDTConditioner::LVDTConditioner(IAdcDriver& adc_driver,
                                float min_range_mm,
                                float max_range_mm,
                                uint16_t default_samples_count)
    : adc_driver_(adc_driver),
      min_range_mm_(min_range_mm),
      max_range_mm_(max_range_mm),
      default_samples_count_(default_samples_count > 0 ? default_samples_count : 1) {}

bool LVDTConditioner::init() {
    return adc_driver_.init();
}

bool LVDTConditioner::read_averaged_voltage(uint16_t sample_count, float& out_avg_voltage) {
    if (sample_count == 0) {
        return false;
    }

    float sum_voltage = 0.0f;
    for (uint16_t i = 0; i < sample_count; ++i) {
        float sample_v = 0.0f;
        if (!adc_driver_.read_voltage(sample_v)) {
            return false;
        }
        sum_voltage += sample_v;
    }

    out_avg_voltage = sum_voltage / static_cast<float>(sample_count);
    return true;
}

bool LVDTConditioner::calibrate_null_point(uint16_t sample_count) {
    float avg_voltage = 0.0f;
    if (!read_averaged_voltage(sample_count, avg_voltage)) {
        cal_data_.is_calibrated = false;
        return false;
    }

    cal_data_.null_voltage_v = avg_voltage;
    cal_data_.is_calibrated = false; // Калібрування незавершене до фіксації другої точки
    return true;
}

bool LVDTConditioner::calibrate_reference_point(float ref_displacement_mm, uint16_t sample_count) {
    if (std::abs(ref_displacement_mm) < 1e-6f) {
        cal_data_.is_calibrated = false;
        return false;
    }

    float avg_voltage = 0.0f;
    if (!read_averaged_voltage(sample_count, avg_voltage)) {
        cal_data_.is_calibrated = false;
        return false;
    }

    cal_data_.ref_voltage_v = avg_voltage;
    cal_data_.ref_displacement_mm = ref_displacement_mm;

    float delta_v = cal_data_.ref_voltage_v - cal_data_.null_voltage_v;
    constexpr float kMinDeltaVoltage = 1e-4f;

    if (std::abs(delta_v) < kMinDeltaVoltage) {
        cal_data_.is_calibrated = false;
        return false;
    }

    // Автоматичний розрахунок коефіцієнта масштабування: K = s_ref / (V_ref - V_null)
    cal_data_.scale_factor_k = cal_data_.ref_displacement_mm / delta_v;
    cal_data_.is_calibrated = true;

    return true;
}

DisplacementResult LVDTConditioner::measure_displacement() {
    DisplacementResult result{};

    float current_voltage = 0.0f;
    if (!read_averaged_voltage(default_samples_count_, current_voltage)) {
        result.status = Status::AdcError;
        result.voltage_v = 0.0f;
        result.displacement_mm = 0.0f;
        return result;
    }

    result.voltage_v = current_voltage;

    if (!cal_data_.is_calibrated) {
        result.status = Status::Uncalibrated;
        result.displacement_mm = 0.0f;
        return result;
    }

    // Перетворення вибірки у точне значення фізичного лінійного зсуву: s = K * (V_diff - V_null)
    float diff_voltage = current_voltage - cal_data_.null_voltage_v;
    float calculated_s = cal_data_.scale_factor_k * diff_voltage;
    result.displacement_mm = calculated_s;

    // Перевірка виходу за робочі межі
    if (calculated_s < min_range_mm_ || calculated_s > max_range_mm_) {
        result.status = Status::OutOfRange;
    } else {
        result.status = Status::OK;
    }

    return result;
}

bool LVDTConditioner::set_calibration_data(const CalibrationData& cal_data) {
    if (!cal_data.is_calibrated) {
        cal_data_ = cal_data;
        cal_data_.is_calibrated = false;
        return false;
    }

    float delta_v = cal_data.ref_voltage_v - cal_data.null_voltage_v;
    if (std::abs(delta_v) < 1e-4f || std::abs(cal_data.scale_factor_k) < 1e-6f) {
        cal_data_.is_calibrated = false;
        return false;
    }

    cal_data_ = cal_data;
    return true;
}

CalibrationData LVDTConditioner::get_calibration_data() const {
    return cal_data_;
}

bool LVDTConditioner::is_calibrated() const {
    return cal_data_.is_calibrated;
}

} // namespace lvdt
