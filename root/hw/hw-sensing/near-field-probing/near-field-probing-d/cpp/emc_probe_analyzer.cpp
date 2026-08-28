// emc_probe_analyzer.cpp - Сканування спектра завад та аналіз гармонік (C++20)
#include <iostream>
#include <vector>
#include <span>
#include <string_view>
#include <cmath>
#include <algorithm>
#include <iomanip>
#include <random>

struct ProbeCalPoint {
    double freq_mhz;
    double af_db;
};

struct SpectralPeak {
    double freq_mhz{};
    double raw_dbm{};
    double corrected_dbuv_m{};
    bool is_over_limit{false};
};

class EmcNearFieldAnalyzer {
public:
    explicit EmcNearFieldAnalyzer(double lna_gain_db = 20.0, double limit_dbuv_m = 40.0)
        : lna_gain_db_{lna_gain_db}, limit_dbuv_m_{limit_dbuv_m} {}

    [[nodiscard]] double get_probe_factor(double freq_mhz) const {
        if (kCalTable.empty()) return 20.0;
        if (freq_mhz <= kCalTable.front().freq_mhz) return kCalTable.front().af_db;
        if (freq_mhz >= kCalTable.back().freq_mhz) return kCalTable.back().af_db;

        auto it = std::lower_bound(kCalTable.begin(), kCalTable.end(), freq_mhz,
            [](const ProbeCalPoint& pt, double val) { return pt.freq_mhz < val; });

        if (it == kCalTable.begin()) return it->af_db;
        const auto& p1 = *it;
        const auto& p0 = *(it - 1);
        return p0.af_db + (p1.af_db - p0.af_db) * (freq_mhz - p0.freq_mhz) / (p1.freq_mhz - p0.freq_mhz);
    }

    [[nodiscard]] double to_field_strength(double raw_dbm, double freq_mhz) const {
        const double dbuv = raw_dbm + 107.0; // 50 Ohm power-to-voltage
        return dbuv - lna_gain_db_ + get_probe_factor(freq_mhz);
    }

    [[nodiscard]] std::vector<SpectralPeak> analyze_spectrum(
        std::span<const double> freqs, std::span<const double> powers_dbm,
        double threshold_dbm = -70.0) const {
        
        std::vector<SpectralPeak> peaks;
        if (freqs.size() != powers_dbm.size() || freqs.size() < 3) return peaks;

        for (size_t i = 1; i < freqs.size() - 1; ++i) {
            if (powers_dbm[i] > powers_dbm[i - 1] &&
                powers_dbm[i] > powers_dbm[i + 1] &&
                powers_dbm[i] >= threshold_dbm) {
                
                const double corrected = to_field_strength(powers_dbm[i], freqs[i]);
                peaks.push_back(SpectralPeak{
                    .freq_mhz = freqs[i],
                    .raw_dbm = powers_dbm[i],
                    .corrected_dbuv_m = corrected,
                    .is_over_limit = (corrected > limit_dbuv_m_)
                });
            }
        }
        return peaks;
    }

    [[nodiscard]] static double detect_fundamental_clock(std::span<const SpectralPeak> peaks) {
        if (peaks.size() < 2) return 0.0;
        double best_delta = 0.0;
        size_t max_matches = 0;

        for (size_t i = 0; i < peaks.size() - 1; ++i) {
            for (size_t j = i + 1; j < peaks.size(); ++j) {
                const double delta = peaks[j].freq_mhz - peaks[i].freq_mhz;
                if (delta < 5.0) continue;

                size_t matches = 0;
                for (const auto& p : peaks) {
                    const double rem = std::fmod(p.freq_mhz + 0.5, delta);
                    if (rem < 1.0 || rem > delta - 1.0) {
                        ++matches;
                    }
                }
                if (matches > max_matches) {
                    max_matches = matches;
                    best_delta = delta;
                }
            }
        }
        return best_delta;
    }

private:
    double lna_gain_db_;
    double limit_dbuv_m_;

    static constexpr std::array<ProbeCalPoint, 7> kCalTable{{
        {  10.0, 32.5 },
        {  30.0, 28.0 },
        {  50.0, 24.5 },
        { 100.0, 20.0 },
        { 200.0, 16.5 },
        { 500.0, 14.0 },
        { 1000.0, 15.5 }
    }};
};

int main() {
    constexpr size_t kPoints = 380;
    constexpr double kFStart = 10.0, kFStop = 200.0;
    std::vector<double> freqs(kPoints);
    std::vector<double> powers(kPoints);

    std::mt19937 gen(42);
    std::uniform_real_distribution<double> noise_dist(-85.0, -82.0);

    for (size_t i = 0; i < kPoints; ++i) {
        freqs[i] = kFStart + static_cast<double>(i) * (kFStop - kFStart) / (kPoints - 1);
        powers[i] = noise_dist(gen);

        // Симуляція гармонік тактового сигналу 25 МГц
        for (double h = 25.0; h <= 200.0; h += 25.0) {
            if (std::abs(freqs[i] - h) < 0.3) {
                powers[i] = -45.0 + (50.0 / (1.0 + (h / 50.0)));
            }
        }
    }

    const EmcNearFieldAnalyzer analyzer(20.0, 40.0);
    const auto peaks = analyzer.analyze_spectrum(freqs, powers, -70.0);

    std::cout << "=== ЗВІТ ЗОНДУВАННЯ БЛИЖНЬОГО ПОЛЯ (NEAR-FIELD SCAN) ===\n";
    std::cout << "Знайдено спектральних піків: " << peaks.size() << "\n";
    std::cout << std::left << std::setw(12) << "Частота"
              << " | " << std::setw(10) << "Рівень"
              << " | " << std::setw(16) << "Напруженість"
              << " | " << "Статус\n";
    std::cout << std::string(57, '-') << "\n";

    for (const auto& p : peaks) {
        std::cout << std::fixed << std::setprecision(2)
                  << std::setw(8) << p.freq_mhz << " МГц | "
                  << std::setw(6) << std::setprecision(1) << p.raw_dbm << " dBm | "
                  << std::setw(6) << p.corrected_dbuv_m << " dBuV/m    | "
                  << (p.is_over_limit ? "FAIL (Перевищення!)" : "PASS") << "\n";
    }

    const double fundamental = EmcNearFieldAnalyzer::detect_fundamental_clock(peaks);
    std::cout << std::string(57, '-') << "\n";
    std::cout << "Ідентифікована базова тактова частота джерела: "
              << std::fixed << std::setprecision(2) << fundamental << " МГц\n";
    if (std::abs(fundamental - 25.0) < 1.0) {
        std::cout << "Ймовірний винуватець: Тактовий генератор 25 МГц Ethernet PHY / USB\n";
    }

    return 0;
}
