#include <iostream>
#include <vector>
#include <span>
#include <cmath>
#include <iomanip>
#include <numbers>

struct PhaseNoisePoint {
    double freq_offset_hz{0.0};  // Частота відступу f_m (Гц)
    double phase_noise_dbc{0.0}; // Спектральна густина L(f_m) (дБн/Гц)
};

struct JitterResult {
    double integrated_phase_noise_rad{0.0}; // RMS фазова похибка (радіани)
    double integrated_phase_noise_deg{0.0}; // RMS фазова похибка (градуси)
    double rms_jitter_sec{0.0};             // RMS часовий джитер (секунди)
    double adc_snr_limit_db{0.0};           // Граничний SNR АЦП (дБ)
    double adc_enob_limit{0.0};             // Гранична розрядність ENOB (біт)
};

class PhaseNoiseIntegrator {
public:
    static double interpolate(double f, std::span<const PhaseNoisePoint> pts) noexcept {
        if (pts.empty()) return 0.0;
        if (f <= pts.front().freq_offset_hz) return pts.front().phase_noise_dbc;
        if (f >= pts.back().freq_offset_hz) return pts.back().phase_noise_dbc;

        for (size_t i = 0; i < pts.size() - 1; ++i) {
            if (f >= pts[i].freq_offset_hz && f <= pts[i + 1].freq_offset_hz) {
                const double f1 = pts[i].freq_offset_hz;
                const double f2 = pts[i + 1].freq_offset_hz;
                const double l1 = pts[i].phase_noise_dbc;
                const double l2 = pts[i + 1].phase_noise_dbc;
                const double slope = (l2 - l1) / std::log10(f2 / f1);
                return l1 + slope * std::log10(f / f1);
            }
        }
        return pts.back().phase_noise_dbc;
    }

    static double integrate_segment(double f1, double l1, double f2, double l2) noexcept {
        if (f2 <= f1 || f1 <= 0.0) return 0.0;

        const double p1 = std::pow(10.0, l1 / 10.0);
        const double p2 = std::pow(10.0, l2 / 10.0);
        const double slope_alpha = std::log10(p2 / p1) / std::log10(f2 / f1);

        if (std::abs(slope_alpha + 1.0) < 1e-5) {
            return p1 * f1 * std::log(f2 / f1);
        } else {
            const double k = p1 / std::pow(f1, slope_alpha);
            const double alpha_plus_1 = slope_alpha + 1.0;
            return (k / alpha_plus_1) * (std::pow(f2, alpha_plus_1) - std::pow(f1, alpha_plus_1));
        }
    }

    static JitterResult calculate(
        std::span<const PhaseNoisePoint> table,
        double carrier_freq_hz,
        double f_start_hz,
        double f_stop_hz,
        double adc_input_freq_hz
    ) noexcept {
        JitterResult res{};
        if (table.size() < 2 || f_start_hz >= f_stop_hz || carrier_freq_hz <= 0.0) {
            return res;
        }

        double total_ssb_power = 0.0;
        double cur_f = f_start_hz;
        double cur_l = interpolate(cur_f, table);

        for (const auto& pt : table) {
            if (pt.freq_offset_hz <= f_start_hz) continue;

            const double next_f = (pt.freq_offset_hz > f_stop_hz) ? f_stop_hz : pt.freq_offset_hz;
            const double next_l = interpolate(next_f, table);

            total_ssb_power += integrate_segment(cur_f, cur_l, next_f, next_l);
            cur_f = next_f;
            cur_l = next_l;

            if (cur_f >= f_stop_hz) break;
        }

        if (cur_f < f_stop_hz) {
            const double next_f = f_stop_hz;
            const double next_l = interpolate(next_f, table);
            total_ssb_power += integrate_segment(cur_f, cur_l, next_f, next_l);
        }

        const double phase_variance = 2.0 * total_ssb_power;
        res.integrated_phase_noise_rad = std::sqrt(phase_variance);
        res.integrated_phase_noise_deg = res.integrated_phase_noise_rad * (180.0 / std::numbers::pi);
        res.rms_jitter_sec = res.integrated_phase_noise_rad / (2.0 * std::numbers::pi * carrier_freq_hz);

        if (adc_input_freq_hz > 0.0 && res.rms_jitter_sec > 0.0) {
            const double snr_linear = 2.0 * std::numbers::pi * adc_input_freq_hz * res.rms_jitter_sec;
            res.adc_snr_limit_db = -20.0 * std::log10(snr_linear);
            res.adc_enob_limit = (res.adc_snr_limit_db - 1.76) / 6.02;
        }

        return res;
    }
};

int main() {
    constexpr std::array<PhaseNoisePoint, 7> ocxo_profile{{
        { 10.0,       -95.0 },
        { 100.0,     -125.0 },
        { 1000.0,    -148.0 },
        { 10000.0,   -160.0 },
        { 100000.0,  -165.0 },
        { 1000000.0, -168.0 },
        { 10000000.0,-170.0 }
    }};

    constexpr double f_carrier = 100.0e6; // 100 МГц
    constexpr double f_start   = 12.0e3;  // 12 кГц
    constexpr double f_stop    = 20.0e6;  // 20 МГц
    constexpr double f_adc_in  = 50.0e6;  // 50 МГц

    const auto res = PhaseNoiseIntegrator::calculate(
        ocxo_profile, f_carrier, f_start, f_stop, f_adc_in
    );

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "================ РЕЗУЛЬТАТИ РОЗРАХУНКУ ДЖИТЕРУ ================\n";
    std::cout << "Несуча частота генератора: " << (f_carrier / 1e6) << " МГц\n";
    std::cout << "Смуга інтегрування шуму:   " << (f_start / 1e3) << " кГц — " << (f_stop / 1e6) << " МГц\n";
    std::cout << "Інтегральний фазовий шум:  " << (res.integrated_phase_noise_rad * 1e3) << " мрад ("
              << res.integrated_phase_noise_deg << " градусів)\n";
    std::cout << std::setprecision(2);
    std::cout << "Середньоквадратичний джитер: " << (res.rms_jitter_sec * 1e15) << " фс ("
              << std::setprecision(5) << (res.rms_jitter_sec * 1e12) << " пс)\n";
    std::cout << "---------------------------------------------------------------\n";
    std::cout << std::setprecision(2);
    std::cout << "Вхідна частота сигналу АЦП: " << (f_adc_in / 1e6) << " МГц\n";
    std::cout << "Теоретична стеля SNR АЦП:   " << res.adc_snr_limit_db << " дБ\n";
    std::cout << "Максимальний ENOB АЦП:      " << res.adc_enob_limit << " біт\n";
    std::cout << "===============================================================\n";

    return 0;
}
