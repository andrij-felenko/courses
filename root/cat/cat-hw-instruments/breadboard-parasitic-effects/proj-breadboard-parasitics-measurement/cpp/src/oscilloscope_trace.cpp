#include "oscilloscope_trace.hpp"

#include <algorithm>
#include <cmath>
#include <numeric>

OscilloscopeTrace::OscilloscopeTrace(std::vector<SamplePoint> samples)
    : samples_(std::move(samples)) {}

void OscilloscopeTrace::addSample(double time_s, double voltage_v) {
    samples_.push_back(SamplePoint{time_s, voltage_v});
}

void OscilloscopeTrace::addSample(const SamplePoint& sample) {
    samples_.push_back(sample);
}

const std::vector<SamplePoint>& OscilloscopeTrace::samples() const noexcept {
    return samples_;
}

std::size_t OscilloscopeTrace::sampleCount() const noexcept {
    return samples_.size();
}

bool OscilloscopeTrace::empty() const noexcept {
    return samples_.empty();
}

void OscilloscopeTrace::clear() noexcept {
    samples_.clear();
}

bool OscilloscopeTrace::validateMonotonicity() const noexcept {
    if (samples_.size() < 2) {
        return true;
    }
    for (std::size_t i = 1; i < samples_.size(); ++i) {
        // Часова шкала повинна бути строго монотонно зростаючою
        if (samples_[i].time_s <= samples_[i - 1].time_s) {
            return false;
        }
    }
    return true;
}

void OscilloscopeTrace::filterOutliers(double max_spike_delta_v) {
    if (samples_.size() < 3) {
        return;
    }

    // Алгоритм виявлення поодиноких імпульсних викидів АЦП:
    // якщо поточна точка різко відхиляється від обох сусідів, замінюємо її
    // середнім значенням сусідів, зберігаючи круті ділянки монотонного фронту.
    for (std::size_t i = 1; i < samples_.size() - 1; ++i) {
        const double v_prev = samples_[i - 1].voltage_v;
        const double v_curr = samples_[i].voltage_v;
        const double v_next = samples_[i + 1].voltage_v;

        const double delta_prev = std::abs(v_curr - v_prev);
        const double delta_next = std::abs(v_curr - v_next);
        const double neighbor_diff = std::abs(v_prev - v_next);

        // Викид: поточна точка далеко від обох сусідів, тоді як сусіди близькі між собою
        if (delta_prev > max_spike_delta_v && delta_next > max_spike_delta_v && neighbor_diff < max_spike_delta_v) {
            samples_[i].voltage_v = 0.5 * (v_prev + v_next);
        }
    }
}

std::optional<std::pair<double, double>> OscilloscopeTrace::calculateAmplitudeLevels() const {
    // Для статистично стабільної оцінки необхідно щонайменше 10 вибірок
    if (samples_.size() < 10) {
        return std::nullopt;
    }

    // Визначаємо розмір вікна для квазістаціонарних ділянок (перші та останні 10% вибірок)
    const std::size_t window_size = std::max<std::size_t>(3, samples_.size() / 10);

    // Усереднення базової лінії (пре-імпульсний стаціонарний стан)
    double baseline_sum = 0.0;
    for (std::size_t i = 0; i < window_size; ++i) {
        baseline_sum += samples_[i].voltage_v;
    }
    const double baseline_v = baseline_sum / static_cast<double>(window_size);

    // Усереднення стаціонарної полиці (пост-імпульсний усталений стан після перехідного процесу)
    double steady_sum = 0.0;
    for (std::size_t i = samples_.size() - window_size; i < samples_.size(); ++i) {
        steady_sum += samples_[i].voltage_v;
    }
    const double steady_state_v = steady_sum / static_cast<double>(window_size);

    // Перевірка наявності змістовної амплітуди перепаду (понад 1 мВ)
    if (std::abs(steady_state_v - baseline_v) < 1.0e-3) {
        return std::nullopt;
    }

    return std::make_pair(baseline_v, steady_state_v);
}

std::optional<double> OscilloscopeTrace::findThresholdCrossingTime(double target_voltage,
                                                                   EdgeSlope slope) const {
    if (samples_.size() < 2) {
        return std::nullopt;
    }

    for (std::size_t i = 0; i < samples_.size() - 1; ++i) {
        const double v1 = samples_[i].voltage_v;
        const double v2 = samples_[i + 1].voltage_v;
        const double t1 = samples_[i].time_s;
        const double t2 = samples_[i + 1].time_s;

        if (slope == EdgeSlope::Rising) {
            // Шукаємо інтервал наростання, що містить порогове значення
            if (v1 <= target_voltage && v2 >= target_voltage && v2 > v1) {
                // Лінійна субдискретна інтерполяція моменту перетину порогу
                const double fraction = (target_voltage - v1) / (v2 - v1);
                return t1 + fraction * (t2 - t1);
            }
        } else {
            // Шукаємо інтервал спаду, що містить порогове значення
            if (v1 >= target_voltage && v2 <= target_voltage && v1 > v2) {
                const double fraction = (v1 - target_voltage) / (v1 - v2);
                return t1 + fraction * (t2 - t1);
            }
        }
    }

    return std::nullopt;
}

std::optional<double> OscilloscopeTrace::calculateRiseTime(double lower_percent,
                                                           double upper_percent) const {
    if (lower_percent >= upper_percent || lower_percent < 0.0 || upper_percent > 1.0) {
        return std::nullopt;
    }

    const auto levels = calculateAmplitudeLevels();
    if (!levels) {
        return std::nullopt;
    }

    const double base_v = levels->first;
    const double top_v = levels->second;

    // Перевіряємо, що сигнал дійсно є наростаючим
    if (top_v <= base_v) {
        return std::nullopt;
    }

    const double amplitude = top_v - base_v;
    const double v_lower = base_v + lower_percent * amplitude;
    const double v_upper = base_v + upper_percent * amplitude;

    const auto t_lower = findThresholdCrossingTime(v_lower, EdgeSlope::Rising);
    const auto t_upper = findThresholdCrossingTime(v_upper, EdgeSlope::Rising);

    if (t_lower && t_upper && *t_upper > *t_lower) {
        return *t_upper - *t_lower;
    }

    return std::nullopt;
}
