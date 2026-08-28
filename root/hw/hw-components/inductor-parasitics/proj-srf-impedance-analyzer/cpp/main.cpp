#include <iostream>
#include <vector>
#include <span>
#include <complex>
#include <cmath>
#include <numbers>
#include <expected>
#include <string_view>
#include <iomanip>

struct VnaSample {
    double freq_hz;
    std::complex<double> s11;
};

struct ExtractedModel {
    double dcr_ohm{0.0};
    double l0_henry{0.0};
    double srf_hz{0.0};
    double epc_farad{0.0};
    double r_peak_ohm{0.0};
    double q_max{0.0};
    double q_max_freq_hz{0.0};
    bool srf_detected{false};
};

enum class ExtractionError {
    InsufficientData,
    InvalidImpedance,
    ZeroFrequency
};

class InductorExtractor {
public:
    static constexpr double DefaultZ0 = 50.0;

    static std::expected<ExtractedModel, ExtractionError> 
    analyze(std::span<const VnaSample> data, double z0 = DefaultZ0) noexcept {
        if (data.size() < 3) {
            return std::unexpected(ExtractionError::InsufficientData);
        }

        ExtractedModel model;
        std::vector<std::pair<double, std::complex<double>>> z_data;
        z_data.reserve(data.size());

        for (const auto& sample : data) {
            if (sample.freq_hz <= 0.0) {
                return std::unexpected(ExtractionError::ZeroFrequency);
            }
            
            auto denom = 1.0 - sample.s11;
            if (std::abs(denom) < 1e-15) {
                return std::unexpected(ExtractionError::InvalidImpedance);
            }
            
            std::complex<double> z = z0 * (1.0 + sample.s11) / denom;
            z_data.emplace_back(sample.freq_hz, z);
        }

        // 1. DCR та L0 на низьких частотах
        model.dcr_ohm = z_data.front().second.real();
        
        for (const auto& [f, z] : z_data) {
            if (z.imag() > 0.0 && f > 10.0) {
                model.l0_henry = z.imag() / (2.0 * std::numbers::pi * f);
                break;
            }
        }

        // 2. Пошук пікової добротності Q та частоти SRF
        for (size_t i = 0; i < z_data.size(); ++i) {
            const auto& [f, z] = z_data[i];
            
            if (z.real() > 1e-9 && z.imag() > 0.0) {
                double q = z.imag() / z.real();
                if (q > model.q_max) {
                    model.q_max = q;
                    model.q_max_freq_hz = f;
                }
            }

            if (i > 0 && !model.srf_detected) {
                const auto& [prev_f, prev_z] = z_data[i - 1];
                if (prev_z.imag() > 0.0 && z.imag() <= 0.0) {
                    double dx = z.imag() - prev_z.imag();
                    double frac = (std::abs(dx) > 1e-12) ? (-prev_z.imag() / dx) : 0.5;
                    model.srf_hz = prev_f + frac * (f - prev_f);
                    model.r_peak_ohm = prev_z.real() + frac * (z.real() - prev_z.real());
                    model.srf_detected = true;
                }
            }
        }

        // 3. Розрахунок EPC
        if (model.srf_detected && model.l0_henry > 0.0 && model.srf_hz > 0.0) {
            double omega = 2.0 * std::numbers::pi * model.srf_hz;
            model.epc_farad = 1.0 / (omega * omega * model.l0_henry);
        }

        return model;
    }
};

int main() {
    const std::vector<VnaSample> sweepData = {
        { 100'000.0,    { 0.0029,  0.0628 } },
        { 1'000'000.0,  { 0.0035,  0.6270 } },
        { 10'000'000.0, { 0.0520,  0.9200 } },
        { 23'720'000.0, { 0.9650,  0.0010 } },
        { 50'000'000.0, { 0.0810, -0.8500 } }
    };

    auto result = InductorExtractor::analyze(sweepData);
    if (result.has_value()) {
        const auto& m = result.value();
        std::cout << std::fixed << std::setprecision(3);
        std::cout << "=== Параметри еквівалентної схеми котушки (C++20) ===\n";
        std::cout << "DCR:             " << m.dcr_ohm << " Ом\n";
        std::cout << "Індуктивність L: " << (m.l0_henry * 1e6) << " мкГн\n";
        if (m.srf_detected) {
            std::cout << "Резонанс SRF:    " << (m.srf_hz / 1e6) << " МГц\n";
            std::cout << "Паразитна EPC:   " << (m.epc_farad * 1e12) << " пФ\n";
            std::cout << "Піковий опір R:  " << (m.r_peak_ohm / 1e3) << " кОм\n";
        }
        std::cout << "Q_max:           " << std::setprecision(1) << m.q_max 
                  << " на частоті " << (m.q_max_freq_hz / 1e6) << " МГц\n";
    }
    return 0;
}
