#include "include/sir_analyzer.hpp"
#include <algorithm>
#include <cmath>
#include <stdexcept>

namespace flux_testing {

SirTimeSeriesAnalyzer::SirTimeSeriesAnalyzer(std::string flux_name, double ipc_threshold_ohms)
    : flux_name_(std::move(flux_name)), ipc_threshold_ohms_(ipc_threshold_ohms) {}

void SirTimeSeriesAnalyzer::add_sample(const SirSample& sample) {
    if (sample.timestamp_hours < 0.0) {
        throw std::invalid_argument("Часова позначка вимірювання не може бути від'ємною.");
    }
    if (sample.resistance_ohms <= 0.0) {
        throw std::invalid_argument("Опір ізоляції повинен бути строгим додатним числом.");
    }
    raw_samples_.push_back(sample);
}

void SirTimeSeriesAnalyzer::add_samples(const std::vector<SirSample>& samples) {
    for (const auto& s : samples) {
        add_sample(s);
    }
}

void SirTimeSeriesAnalyzer::clear() {
    raw_samples_.clear();
}

std::vector<SirSample> SirTimeSeriesAnalyzer::filter_median_noise(std::size_t window_size) const {
    if (raw_samples_.empty()) {
        return {};
    }
    if (window_size % 2 == 0 || window_size < 1) {
        throw std::invalid_argument("Розмір вікна медіанного фільтра повинен бути непарним додатним числом.");
    }

    const std::size_t n = raw_samples_.size();
    std::vector<SirSample> filtered = raw_samples_;
    const std::size_t half_win = window_size / 2;

    for (std::size_t i = 0; i < n; ++i) {
        std::size_t start_idx = (i >= half_win) ? (i - half_win) : 0;
        std::size_t end_idx = std::min(n - 1, i + half_win);

        std::vector<double> window_values;
        window_values.reserve(end_idx - start_idx + 1);

        for (std::size_t j = start_idx; j <= end_idx; ++j) {
            window_values.push_back(raw_samples_[j].resistance_ohms);
        }

        std::sort(window_values.begin(), window_values.end());
        
        std::size_t mid = window_values.size() / 2;
        double median_val = (window_values.size() % 2 != 0) 
            ? window_values[mid] 
            : (window_values[mid - 1] + window_values[mid]) / 2.0;

        filtered[i].resistance_ohms = median_val;
    }

    return filtered;
}

std::vector<LocalMinimum> SirTimeSeriesAnalyzer::detect_local_minima(
    const std::vector<SirSample>& filtered_samples, 
    double dip_threshold_pct) const {

    std::vector<LocalMinimum> minima;
    if (filtered_samples.size() < 3) {
        return minima;
    }

    for (std::size_t i = 1; i < filtered_samples.size() - 1; ++i) {
        double prev_r = filtered_samples[i - 1].resistance_ohms;
        double curr_r = filtered_samples[i].resistance_ohms;
        double next_r = filtered_samples[i + 1].resistance_ohms;

        if (curr_r < prev_r && curr_r < next_r) {
            double avg_neighbor = (prev_r + next_r) / 2.0;
            double dip_pct = ((avg_neighbor - curr_r) / avg_neighbor) * 100.0;

            if (dip_pct >= dip_threshold_pct) {
                LocalMinimum min_point;
                min_point.timestamp_hours = filtered_samples[i].timestamp_hours;
                min_point.resistance_ohms = curr_r;
                min_point.depth_ratio = dip_pct;
                minima.push_back(min_point);
            }
        }
    }

    return minima;
}

SirReport SirTimeSeriesAnalyzer::generate_report(std::size_t median_window) const {
    if (raw_samples_.empty()) {
        throw std::runtime_error("Неможливо згенерувати звіт: часовий ряд вимірювань порожній.");
    }

    std::vector<SirSample> filtered = filter_median_noise(median_window);

    SirReport report;
    report.flux_name = flux_name_;
    report.total_samples = filtered.size();
    report.initial_sir_ohms = filtered.front().resistance_ohms;
    report.final_sir_ohms = filtered.back().resistance_ohms;
    report.ipc_threshold_ohms = ipc_threshold_ohms_;

    double global_min = filtered.front().resistance_ohms;
    for (const auto& s : filtered) {
        if (s.resistance_ohms < global_min) {
            global_min = s.resistance_ohms;
        }
    }
    report.global_min_ohms = global_min;
    report.local_minima = detect_local_minima(filtered, 15.0);
    report.is_ipc_compliant = (report.global_min_ohms >= report.ipc_threshold_ohms);

    bool significant_drop = false;
    if (filtered.size() > 5) {
        double baseline_r = filtered[std::min<std::size_t>(filtered.size() / 4, filtered.size() - 1)].resistance_ohms;
        if (report.final_sir_ohms < (baseline_r / 10.0)) {
            significant_drop = true;
        }
    }

    report.dendrite_growth_risk = (!report.is_ipc_compliant || significant_drop);

    return report;
}

} // namespace flux_testing
