#include "waveform_analyzer.hpp"
#include <cmath>
#include <numeric>
#include <algorithm>
#include <stdexcept>

WaveformAnalyzer::WaveformAnalyzer(double sample_rate_hz, double clip_threshold_v)
    : sample_rate_hz_(sample_rate_hz), clip_threshold_v_(clip_threshold_v) {
    if (sample_rate_hz_ <= 0.0) {
        throw std::invalid_argument("Частота дискретизації має бути додатною");
    }
}

WaveformMetrics WaveformAnalyzer::analyze_channel(std::span<const double> samples) const {
    if (samples.size() < 4) {
        return {};
    }

    WaveformMetrics metrics;
    
    // 1. Пошук мінімуму та максимуму
    auto [min_it, max_it] = std::minmax_element(samples.begin(), samples.end());
    metrics.v_min = *min_it;
    metrics.v_max = *max_it;
    metrics.v_pp = metrics.v_max - metrics.v_min;

    // 2. Розрахунок постійного зсуву (DC offset) та V_rms
    const double dc_offset = std::accumulate(samples.begin(), samples.end(), 0.0) / static_cast<double>(samples.size());
    double sum_sq_ac = 0.0;
    for (const double val : samples) {
        const double ac_component = val - dc_offset;
        sum_sq_ac += ac_component * ac_component;
    }
    metrics.v_rms = std::sqrt(sum_sq_ac / static_cast<double>(samples.size()));

    // 3. Детекція кліпінгу: перевірка утримання сигналу біля порогу АЦП
    std::size_t consecutive_clip = 0;
    for (const double val : samples) {
        if (std::abs(val) >= clip_threshold_v_) {
            consecutive_clip++;
            if (consecutive_clip >= 3) {
                metrics.is_clipped = true;
                break;
            }
        } else {
            consecutive_clip = 0;
        }
    }

    // 4. Оцінка частоти за інтервалами перетинів нульового рівня (DC offset)
    const double z1 = find_first_rising_zero_crossing(samples, dc_offset);
    if (z1 >= 0.0 && (z1 + 1.0) < static_cast<double>(samples.size())) {
        const double z2 = find_first_rising_zero_crossing(samples.subspan(static_cast<std::size_t>(z1 + 1.0)), dc_offset);
        if (z2 >= 0.0) {
            const double period_samples = (z1 + 1.0 + z2) - z1;
            if (period_samples > 0.0) {
                metrics.frequency_hz = sample_rate_hz_ / period_samples;
            }
        }
    }

    return metrics;
}

double WaveformAnalyzer::find_first_rising_zero_crossing(std::span<const double> samples, double offset_v) const {
    for (std::size_t i = 0; i + 1 < samples.size(); ++i) {
        const double y1 = samples[i] - offset_v;
        const double y2 = samples[i + 1] - offset_v;
        
        // Виявлення висхідного фронту через нульову лінію
        if (y1 <= 0.0 && y2 > 0.0) {
            // Лінійна інтерполяція дробової частини відліку
            const double fraction = -y1 / (y2 - y1);
            return static_cast<double>(i) + fraction;
        }
    }
    return -1.0;
}

DualChannelResult WaveformAnalyzer::analyze_dual(std::span<const double> ch1_samples,
                                                 std::span<const double> ch2_samples) const {
    if (ch1_samples.size() != ch2_samples.size()) {
        throw std::invalid_argument("Буфери CH1 та CH2 повинні мати однакову довжину");
    }

    DualChannelResult result;
    result.ch1_metrics = analyze_channel(ch1_samples);
    result.ch2_metrics = analyze_channel(ch2_samples);

    // Розрахунок коефіцієнта підсилення
    if (result.ch1_metrics.v_pp > 1e-6) {
        result.gain_linear = result.ch2_metrics.v_pp / result.ch1_metrics.v_pp;
        result.gain_db = 20.0 * std::log10(result.gain_linear);
    }

    // Обчислення фазового зсуву за першими висхідними перетинами нуля
    const double dc1 = (result.ch1_metrics.v_max + result.ch1_metrics.v_min) / 2.0;
    const double dc2 = (result.ch2_metrics.v_max + result.ch2_metrics.v_min) / 2.0;

    const double t1_idx = find_first_rising_zero_crossing(ch1_samples, dc1);
    const double t2_idx = find_first_rising_zero_crossing(ch2_samples, dc2);

    if (t1_idx >= 0.0 && t2_idx >= 0.0 && result.ch1_metrics.frequency_hz > 0.0) {
        const double delta_samples = t2_idx - t1_idx;
        result.time_delay_s = delta_samples / sample_rate_hz_;
        
        // Переведення часового зсуву у фазовий кут: Δφ = 360° * f * Δt
        double phase = 360.0 * result.ch1_metrics.frequency_hz * result.time_delay_s;
        
        // Нормалізація в діапазон [-180°, +180°]
        while (phase > 180.0) phase -= 360.0;
        while (phase < -180.0) phase += 360.0;
        result.phase_shift_deg = phase;
    }

    return result;
}
