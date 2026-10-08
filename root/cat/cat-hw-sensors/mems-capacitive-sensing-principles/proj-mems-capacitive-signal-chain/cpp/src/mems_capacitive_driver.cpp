#include "mems_capacitive_driver.hpp"
#include <algorithm>
#include <cmath>

namespace mems {

MemsCapacitiveDriver::MemsCapacitiveDriver(IMemsHardwareAdapter& hw_adapter,
                                           CapacitiveSensingConfig config)
    : hw_adapter_(hw_adapter), config_(config) {}

bool MemsCapacitiveDriver::initialize() {
    if (!hw_adapter_.configure_excitation(config_.excitation_freq_hz)) {
        return false;
    }

    if (!hw_adapter_.set_excitation_enabled(true)) {
        return false;
    }

    // Скидаємо початкове значення ЦАП компенсації в нуль
    if (!hw_adapter_.set_dac_offset_voltage(0.0f)) {
        return false;
    }

    baseline_offset_v_ = 0.0f;
    filter_state_v_ = 0.0f;
    last_raw_v_ = 0.0f;
    last_demod_v_ = 0.0f;
    last_filtered_v_ = 0.0f;
    calibration_status_ = CalibrationStatus::NotCalibrated;
    initialized_ = true;

    return true;
}

CalibrationStatus MemsCapacitiveDriver::calibrate_baseline() {
    if (!initialized_) {
        calibration_status_ = CalibrationStatus::ErrorHardwareFault;
        return calibration_status_;
    }

    if (config_.calibration_samples == 0) {
        calibration_status_ = CalibrationStatus::ErrorInvalidSamples;
        return calibration_status_;
    }

    calibration_status_ = CalibrationStatus::InProgress;
    float accumulated_demod_sum = 0.0f;

    // Виконуємо усреднення вибірок у стані спокою MEMS-структури
    for (std::size_t i = 0; i < config_.calibration_samples; ++i) {
        float raw_adc = hw_adapter_.read_adc_voltage();
        ExcitationPhase phase = hw_adapter_.current_excitation_phase();

        float multiplier = 1.0f;
        if (demod_mode_ == DemodulationMode::SynchronousInPhase) {
            multiplier = (phase == ExcitationPhase::Phase0) ? 1.0f : -1.0f;
        } else {
            multiplier = (phase == ExcitationPhase::Phase0) ? -1.0f : 1.0f;
        }

        float demodulated = raw_adc * multiplier;
        accumulated_demod_sum += demodulated;
    }

    float calculated_baseline = accumulated_demod_sum / static_cast<float>(config_.calibration_samples);

    // Перевірка на перевищення максимально допустимого паразитичного зсуву
    if (std::abs(calculated_baseline) > config_.max_allowed_baseline_drift_v) {
        calibration_status_ = CalibrationStatus::ErrorDriftExceeded;
        return calibration_status_;
    }

    baseline_offset_v_ = calculated_baseline;
    filter_state_v_ = 0.0f; // Скидаємо стан фільтра після калібрування
    calibration_status_ = CalibrationStatus::Success;

    // Спроба апаратно компенсувати постійну складову через ЦАП (якщо підтримується)
    hw_adapter_.set_dac_offset_voltage(baseline_offset_v_);

    return calibration_status_;
}

float MemsCapacitiveDriver::process_sample() {
    if (!initialized_) {
        return 0.0f;
    }

    // 1. Зчитування сирого аналогового сигналу з підсилювача заряду
    last_raw_v_ = hw_adapter_.read_adc_voltage();
    ExcitationPhase phase = hw_adapter_.current_excitation_phase();

    // 2. Синхронна фазова демодуляція (down-conversion носія до базової смуги)
    float phase_multiplier = 1.0f;
    if (demod_mode_ == DemodulationMode::SynchronousInPhase) {
        phase_multiplier = (phase == ExcitationPhase::Phase0) ? 1.0f : -1.0f;
    } else {
        phase_multiplier = (phase == ExcitationPhase::Phase0) ? -1.0f : 1.0f;
    }

    last_demod_v_ = last_raw_v_ * phase_multiplier;

    // 3. Віднімання каліброваного початкового z-зсуву (baseline)
    float zero_corrected = last_demod_v_ - baseline_offset_v_;

    // 4. Цифрова фільтрація низьких частот (рекурсивний ФНЧ першого порядку)
    filter_state_v_ = config_.lpf_alpha * zero_corrected + (1.0f - config_.lpf_alpha) * filter_state_v_;
    last_filtered_v_ = filter_state_v_;

    return last_filtered_v_;
}

float MemsCapacitiveDriver::get_capacitance_delta_pf() const noexcept {
    // Перетворення компенсаційної напруги у зміну ємності (pF)
    return last_filtered_v_ * config_.sensitivity_pf_per_volt;
}

float MemsCapacitiveDriver::get_displacement_um() const noexcept {
    // Обчислення зсуву обкладок (мкм) через розраховану зміну ємності
    float delta_pf = get_capacitance_delta_pf();
    return delta_pf * config_.scale_factor_um_per_pf;
}

float MemsCapacitiveDriver::get_baseline_offset_v() const noexcept {
    return baseline_offset_v_;
}

CalibrationStatus MemsCapacitiveDriver::get_calibration_status() const noexcept {
    return calibration_status_;
}

void MemsCapacitiveDriver::set_demodulation_mode(DemodulationMode mode) noexcept {
    demod_mode_ = mode;
}

void MemsCapacitiveDriver::set_lpf_alpha(float alpha) {
    config_.lpf_alpha = std::clamp(alpha, 0.001f, 1.0f);
}

float MemsCapacitiveDriver::get_last_raw_voltage() const noexcept {
    return last_raw_v_;
}

float MemsCapacitiveDriver::get_last_demodulated_voltage() const noexcept {
    return last_demod_v_;
}

float MemsCapacitiveDriver::get_last_filtered_voltage() const noexcept {
    return last_filtered_v_;
}

} // namespace mems
