#include <iostream>
#include <vector>
#include <complex>
#include <cmath>
#include <span>
#include <optional>
#include <random>
#include <string_view>

struct MultipathRay {
    double delay_ns{0.0};     // Затримка променя в наносекундах
    double power_linear{0.0}; // Лінійна потужність променя
    double phase_rad{0.0};    // Фаза променя в радіанах
};

struct PdpMetrics {
    double total_power{0.0};   // Сумарна потужність
    double mean_delay_ns{0.0}; // Середня затримка τ̄ (нс)
    double rms_spread_ns{0.0}; // RMS delay spread σ_τ (нс)
    double bc_50_mhz{0.0};     // Смуга когерентності B_c (50%), МГц
    double bc_90_mhz{0.0};     // Смуга когерентності B_c (90%), МГц
    bool is_flat_fading{false}; // true якщо B_s < B_c
};

using ComplexD = std::complex<double>;

// Обчислення метрик PDP каналу
[[nodiscard]] std::optional<PdpMetrics> calculate_pdp_metrics(
    std::span<const MultipathRay> rays, 
    double signal_bw_mhz) noexcept 
{
    if (rays.empty()) {
        return std::nullopt;
    }

    double p_total = 0.0;
    double weighted_delay_sum = 0.0;
    double weighted_delay_sq_sum = 0.0;

    for (const auto& ray : rays) {
        if (ray.power_linear < 0.0 || ray.delay_ns < 0.0) {
            return std::nullopt;
        }
        p_total += ray.power_linear;
        weighted_delay_sum += ray.power_linear * ray.delay_ns;
        weighted_delay_sq_sum += ray.power_linear * ray.delay_ns * ray.delay_ns;
    }

    if (p_total <= 0.0) {
        return std::nullopt;
    }

    const double tau_mean = weighted_delay_sum / p_total;
    const double tau_sq_mean = weighted_delay_sq_sum / p_total;
    const double variance = tau_sq_mean - (tau_mean * tau_mean);

    const double rms_spread = (variance > 0.0) ? std::sqrt(variance) : 0.0;

    PdpMetrics metrics;
    metrics.total_power = p_total;
    metrics.mean_delay_ns = tau_mean;
    metrics.rms_spread_ns = rms_spread;

    if (rms_spread > 0.0) {
        metrics.bc_50_mhz = 1000.0 / (5.0 * rms_spread);
        metrics.bc_90_mhz = 1000.0 / (50.0 * rms_spread);
    } else {
        metrics.bc_50_mhz = 1e9;
        metrics.bc_90_mhz = 1e9;
    }

    metrics.is_flat_fading = (signal_bw_mhz < metrics.bc_50_mhz);
    return metrics;
}

// Симуляція міжсимвольної інтерференції (ISI)
[[nodiscard]] std::vector<ComplexD> simulate_channel_isi(
    std::span<const ComplexD> in_symbols,
    std::span<const MultipathRay> rays,
    double symbol_duration_ns) 
{
    std::vector<ComplexD> out_symbols(in_symbols.size(), ComplexD{0.0, 0.0});

    for (size_t n = 0; n < in_symbols.size(); ++n) {
        ComplexD rx_sample{0.0, 0.0};
        
        for (const auto& ray : rays) {
            const double ray_delay_sym = ray.delay_ns / symbol_duration_ns;
            const auto tap_delay = static_cast<size_t>(std::round(ray_delay_sym));
            
            if (n >= tap_delay) {
                const double amp = std::sqrt(ray.power_linear);
                const ComplexD phase_rot = std::polar(amp, ray.phase_rad);
                rx_sample += in_symbols[n - tap_delay] * phase_rot;
            }
        }
        out_symbols[n] = rx_sample;
    }
    return out_symbols;
}

// Розрахунок помилок SER для QPSK
[[nodiscard]] double calculate_qpsk_ser(
    std::span<const ComplexD> tx, 
    std::span<const ComplexD> rx) noexcept 
{
    size_t errors = 0;
    const size_t count = std::min(tx.size(), rx.size());

    for (size_t i = 0; i < count; ++i) {
        const int tx_re = (tx[i].real() > 0.0) ? 1 : -1;
        const int tx_im = (tx[i].imag() > 0.0) ? 1 : -1;
        
        const int rx_re = (rx[i].real() > 0.0) ? 1 : -1;
        const int rx_im = (rx[i].imag() > 0.0) ? 1 : -1;

        if (tx_re != rx_re || tx_im != rx_im) {
            errors++;
        }
    }
    return static_cast<double>(errors) / static_cast<double>(count);
}

int main() {
    const std::vector<MultipathRay> veh_a_profile{
        {   0.0, 1.000, 0.00 },
        { 310.0, 0.794, 0.85 },
        { 710.0, 0.126, 1.42 },
        {1090.0, 0.032, 2.10 },
        {1730.0, 0.010, 2.85 },
        {2510.0, 0.003, 3.14 }
    };
    constexpr size_t symbol_count = 1000;
    constexpr double signal_bw_mhz = 20.0;

    std::cout << "=== КАЛЬКУЛЯТОР ПРОФІЛЮ ЗАТРИМОК ТА СИМУЛЯТОР ISI (C++) ===\n\n";

    if (const auto metrics = calculate_pdp_metrics(veh_a_profile, signal_bw_mhz)) {
        std::cout << "Повна потужність P_total: " << metrics->total_power << '\n'
                  << "Середня затримка (tau_bar): " << metrics->mean_delay_ns << " нс\n"
                  << "RMS Delay Spread (sigma_tau): " << metrics->rms_spread_ns << " нс\n"
                  << "Смуга когерентності B_c (50%): " << metrics->bc_50_mhz << " МГц\n"
                  << "Смуга когерентності B_c (90%): " << metrics->bc_90_mhz << " МГц\n"
                  << "Режим завмирання: " 
                  << (metrics->is_flat_fading ? "Плоске (Frequency-flat)" : "Частотно-селективне (Frequency-selective)") 
                  << "\n\n";
    }

    // Генерація випадкових QPSK символів
    std::mt19937 rng(42);
    std::bernoulli_distribution dist(0.5);

    std::vector<ComplexD> tx_symbols(symbol_count);
    for (auto& sym : tx_symbols) {
        const double re = dist(rng) ? 1.0 : -1.0;
        const double im = dist(rng) ? 1.0 : -1.0;
        sym = ComplexD{re, im} / std::sqrt(2.0);
    }

    // Повільна передача (T_s = 10 мкс >> tau_max)
    const auto rx_slow = simulate_channel_isi(tx_symbols, veh_a_profile, 10000.0);
    const double ser_slow = calculate_qpsk_ser(tx_symbols, rx_slow);
    std::cout << "Повільна передача (T_s = 10 мкс, T_s >> tau_max): QPSK SER = " << ser_slow << " (Немає ISI)\n";

    // Швидка передача (T_s = 0.5 мкс < tau_max)
    const auto rx_fast = simulate_channel_isi(tx_symbols, veh_a_profile, 500.0);
    const double ser_fast = calculate_qpsk_ser(tx_symbols, rx_fast);
    std::cout << "Швидка передача (T_s = 0.5 мкс, T_s < tau_max): QPSK SER = " << ser_fast << " (Важка ISI!)\n";

    return 0;
}
