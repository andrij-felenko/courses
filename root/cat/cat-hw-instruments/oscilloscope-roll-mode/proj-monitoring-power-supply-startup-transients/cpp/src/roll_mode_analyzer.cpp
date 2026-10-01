#include "roll_mode_analyzer.hpp"
#include <cmath>
#include <utility>

namespace roll_mode {

RollModeAnalyzer::RollModeAnalyzer(std::vector<Sample> samples)
    : m_samples(std::move(samples)) {}

void RollModeAnalyzer::addSample(const Sample& sample) {
    m_samples.push_back(sample);
}

const std::vector<Sample>& RollModeAnalyzer::getSamples() const noexcept {
    return m_samples;
}

StabilizationResult RollModeAnalyzer::analyzeStabilization(
    double steady_voltage,
    double tolerance_pct
) const {
    StabilizationResult result;
    result.steady_voltage_v = steady_voltage;

    if (m_samples.size() < 2 || tolerance_pct < 0.0) {
        return result;
    }

    const double delta_v = std::abs(steady_voltage * (tolerance_pct / 100.0));
    const double v_min = steady_voltage - delta_v;
    const double v_max = steady_voltage + delta_v;

    const double t0 = m_samples.front().timestamp_sec;
    std::size_t last_out_of_bounds_index = 0;
    bool found_out_of_bounds = false;

    for (std::size_t i = 0; i < m_samples.size(); ++i) {
        if (m_samples[i].voltage_v < v_min || m_samples[i].voltage_v > v_max) {
            last_out_of_bounds_index = i;
            found_out_of_bounds = true;
        }
    }

    result.is_stabilized = true;
    if (!found_out_of_bounds) {
        // Сигнал перебував у коридорі з найпершого відліку
        result.settling_time_sec = 0.0;
    } else {
        // Тривалість розраховується від початкового моменту t0 до останнього порушення меж
        result.settling_time_sec = m_samples[last_out_of_bounds_index].timestamp_sec - t0;
    }

    return result;
}

BatteryDischargeResult RollModeAnalyzer::calculateDischargedCapacity() const {
    BatteryDischargeResult result{};

    if (m_samples.size() < 2) {
        return result;
    }

    double total_amp_seconds = 0.0;
    double total_watt_seconds = 0.0;

    // Чисельне інтегрування методом трапецій по всьому масиву Roll Mode
    for (std::size_t i = 1; i < m_samples.size(); ++i) {
        const auto& prev = m_samples[i - 1];
        const auto& curr = m_samples[i];

        const double dt = curr.timestamp_sec - prev.timestamp_sec;
        if (dt <= 0.0) {
            continue; // Пропускаємо некоректні часові кроки
        }

        // Середній струм на інтервалі (A)
        const double avg_current = (prev.current_a + curr.current_a) / 2.0;
        // Середня потужність на інтервалі (W = V * I)
        const double prev_power = prev.voltage_v * prev.current_a;
        const double curr_power = curr.voltage_v * curr.current_a;
        const double avg_power = (prev_power + curr_power) / 2.0;

        total_amp_seconds += avg_current * dt;
        total_watt_seconds += avg_power * dt;
    }

    result.total_time_sec = m_samples.back().timestamp_sec - m_samples.front().timestamp_sec;
    // Переведення секунди -> години (1 година = 3600 секунд)
    result.capacity_amp_hours = total_amp_seconds / 3600.0;
    result.energy_watt_hours = total_watt_seconds / 3600.0;

    return result;
}

} // namespace roll_mode
