#include "optical_power_meter.hpp"
#include <cmath>
#include <algorithm>
#include <numeric>

namespace opm {

OpticalPowerMeter::OpticalPowerMeter(HardwareConfig config, std::vector<CalibPoint> calib_table)
    : config_(config), calib_table_(std::move(calib_table)) {
    // Впорядкування калібрувальної таблиці за довжиною хвилі
    std::sort(calib_table_.begin(), calib_table_.end(), [](const CalibPoint& a, const CalibPoint& b) {
        return a.wavelength_nm < b.wavelength_nm;
    });

    if (!calib_table_.empty()) {
        setWavelength(calib_table_.front().wavelength_nm);
    }
}

bool OpticalPowerMeter::setWavelength(std::uint16_t wavelength_nm) {
    if (calib_table_.empty()) {
        return false;
    }

    if (wavelength_nm < calib_table_.front().wavelength_nm ||
        wavelength_nm > calib_table_.back().wavelength_nm) {
        return false;
    }

    current_sensitivity_a_w_ = interpolateSensitivity(wavelength_nm);
    current_wavelength_nm_ = wavelength_nm;
    return true;
}

float OpticalPowerMeter::interpolateSensitivity(std::uint16_t wavelength_nm) const {
    if (wavelength_nm <= calib_table_.front().wavelength_nm) {
        return calib_table_.front().sensitivity_a_w;
    }
    if (wavelength_nm >= calib_table_.back().wavelength_nm) {
        return calib_table_.back().sensitivity_a_w;
    }

    // Пошук інтервалу для лінійної інтерполяції
    auto it = std::upper_bound(calib_table_.begin(), calib_table_.end(), wavelength_nm,
        [](std::uint16_t val, const CalibPoint& pt) {
            return val < pt.wavelength_nm;
        });

    const auto& pt2 = *it;
    const auto& pt1 = *(it - 1);

    const float slope = (pt2.sensitivity_a_w - pt1.sensitivity_a_w) /
                        static_cast<float>(pt2.wavelength_nm - pt1.wavelength_nm);

    return pt1.sensitivity_a_w + slope * static_cast<float>(wavelength_nm - pt1.wavelength_nm);
}

bool OpticalPowerMeter::calibrateDarkOffset(const std::vector<std::uint16_t>& dark_adc_samples) {
    if (dark_adc_samples.empty()) {
        return false;
    }

    const std::uint64_t sum = std::accumulate(dark_adc_samples.begin(), dark_adc_samples.end(), 0ULL);
    const float avg_adc = static_cast<float>(sum) / static_cast<float>(dark_adc_samples.size());

    // Обчислення напруги зсуву темряви
    dark_offset_v_ = (avg_adc / static_cast<float>(config_.adc_max_count)) * config_.adc_vref_v;
    return true;
}

std::optional<MeasurementResult> OpticalPowerMeter::processAdcSample(std::uint16_t raw_adc_sample) {
    if (current_sensitivity_a_w_ <= 0.0f) {
        return std::nullopt;
    }

    // Проста цифрова фільтрація ковзним вікном (розмір 16)
    constexpr std::size_t kWindowSize = 16;
    if (filter_buffer_.size() < kWindowSize) {
        filter_buffer_.push_back(raw_adc_sample);
    } else {
        filter_buffer_[filter_index_] = raw_adc_sample;
        filter_index_ = (filter_index_ + 1) % kWindowSize;
    }

    const std::uint64_t sum = std::accumulate(filter_buffer_.begin(), filter_buffer_.end(), 0ULL);
    const float filtered_adc = static_cast<float>(sum) / static_cast<float>(filter_buffer_.size());

    // 1. Конверсія відліків АЦП у напругу TIA
    const float raw_voltage = (filtered_adc / static_cast<float>(config_.adc_max_count)) * config_.adc_vref_v;

    // 2. Компенсація темнового струму (Dark Offset Subtraction)
    float signal_voltage = raw_voltage - dark_offset_v_;
    if (signal_voltage < 0.0f) {
        signal_voltage = 0.0f;
    }

    // 3. Розрахунок фотоструму I_ph = V_sig / Rf
    const float photocurrent_a = signal_voltage / config_.tia_gain_ohm;

    // 4. Обчислення оптичної потужності P = I_ph / R(λ)
    MeasurementResult res;
    res.power_w = photocurrent_a / current_sensitivity_a_w_;
    res.power_dbm = wattsToDbm(res.power_w);
    res.lidt_exceeded = (res.power_w >= config_.lidt_max_power_w);

    return res;
}

float OpticalPowerMeter::wattsToDbm(float power_w) noexcept {
    if (power_w <= 1e-15f) {
        return -120.0f;
    }
    return 10.0f * std::log10(power_w / 0.001f);
}

} // namespace opm
