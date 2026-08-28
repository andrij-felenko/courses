#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <algorithm>
#include <iomanip>
#include <stdexcept>

struct SpectralLine {
    double wavelength_nm;
    double intensity;
};

struct SpectrumPoint {
    double angle_deg;
    double total_intensity;
};

struct ResolutionResult {
    bool resolved;
    double contrast;
    double peak1_deg;
    double peak2_deg;
};

class DiffractionGratingSimulator {
public:
    DiffractionGratingSimulator(double grooves_per_mm, double slit_width_um, int num_grooves)
        : period_m_(1.0e-3 / grooves_per_mm),
          slit_width_m_(slit_width_um * 1.0e-6),
          num_grooves_(num_grooves) {
        if (grooves_per_mm <= 0.0 || slit_width_um <= 0.0 || num_grooves <= 0) {
            throw std::invalid_argument("Некоректні вхідні параметри ґратки.");
        }
    }

    double compute_point_intensity(double theta_rad, const std::vector<SpectralLine>& lines) const {
        const double sin_theta = std::sin(theta_rad);
        double total_intensity = 0.0;

        for (const auto& line : lines) {
            const double lam = line.wavelength_nm * 1.0e-9;

            // 1. Однощілинна обвідна
            const double beta = (std::numbers::pi * slit_width_m_ * sin_theta) / lam;
            const double envelope = (std::abs(beta) < 1.0e-9)
                ? 1.0
                : std::pow(std::sin(beta) / beta, 2.0);

            // 2. Інтерференційний множник N щілин
            const double gamma = (std::numbers::pi * period_m_ * sin_theta) / lam;
            const double sin_gamma = std::sin(gamma);

            double interference = 0.0;
            if (std::abs(sin_gamma) < 1.0e-9) {
                const double N_dbl = static_cast<double>(num_grooves_);
                interference = N_dbl * N_dbl;
            } else {
                const double sin_N_gamma = std::sin(num_grooves_ * gamma);
                interference = std::pow(sin_N_gamma / sin_gamma, 2.0);
            }

            total_intensity += line.intensity * envelope * interference;
        }

        return total_intensity;
    }

    std::vector<SpectrumPoint> scan_spectrum(const std::vector<SpectralLine>& lines,
                                            double start_deg = -89.0,
                                            double end_deg = 89.0,
                                            double step_deg = 0.01) const {
        std::vector<SpectrumPoint> spectrum;
        const size_t estimated_size = static_cast<size_t>((end_deg - start_deg) / step_deg) + 1;
        spectrum.reserve(estimated_size);

        for (double curr_deg = start_deg; curr_deg <= end_deg; curr_deg += step_deg) {
            const double theta_rad = curr_deg * std::numbers::pi / 180.0;
            const double intensity = compute_point_intensity(theta_rad, lines);
            spectrum.push_back({curr_deg, intensity});
        }

        return spectrum;
    }

private:
    double period_m_;
    double slit_width_m_;
    int num_grooves_;
};

ResolutionResult analyze_doublet_resolution(const std::vector<SpectrumPoint>& spectrum,
                                            double search_min_deg,
                                            double search_max_deg) {
    std::vector<SpectrumPoint> region;
    for (const auto& pt : spectrum) {
        if (pt.angle_deg >= search_min_deg && pt.angle_deg <= search_max_deg) {
            region.push_back(pt);
        }
    }

    if (region.size() < 3) {
        return {false, 0.0, 0.0, 0.0};
    }

    std::vector<SpectrumPoint> peaks;
    for (size_t i = 1; i < region.size() - 1; ++i) {
        if (region[i].total_intensity > region[i - 1].total_intensity &&
            region[i].total_intensity > region[i + 1].total_intensity) {
            peaks.push_back(region[i]);
        }
    }

    if (peaks.size() < 2) {
        return {false, 0.0, 0.0, 0.0};
    }

    std::sort(peaks.begin(), peaks.end(), [](const SpectrumPoint& a, const SpectrumPoint& b) {
        return a.total_intensity > b.total_intensity;
    });

    const auto p1 = peaks[0];
    const auto p2 = peaks[1];
    const double min_angle = std::min(p1.angle_deg, p2.angle_deg);
    const double max_angle = std::max(p1.angle_deg, p2.angle_deg);

    double min_val = p1.total_intensity;
    for (const auto& pt : region) {
        if (pt.angle_deg >= min_angle && pt.angle_deg <= max_angle) {
            min_val = std::min(min_val, pt.total_intensity);
        }
    }

    const double max_val = std::min(p1.total_intensity, p2.total_intensity);
    const double contrast = (max_val > 0.0) ? (max_val - min_val) / max_val : 0.0;
    const bool resolved = contrast >= 0.19;

    return {resolved, contrast, p1.angle_deg, p2.angle_deg};
}

int main() {
    try {
        const std::vector<SpectralLine> sodium_doublet = {
            {589.0, 1.0},
            {589.6, 0.8}
        };

        DiffractionGratingSimulator sim(600.0, 0.5, 1000);
        auto spectrum = sim.scan_spectrum(sodium_doublet, 20.0, 21.5, 0.002);

        auto res = analyze_doublet_resolution(spectrum, 20.0, 21.5);
        std::cout << std::fixed << std::setprecision(3);
        std::cout << "Результат симуляції натрієвого дублета (N = 1000):\n";
        std::cout << "  Розділення за Релеєм: " << (res.resolved ? "ТАК" : "НІ") << "\n";
        std::cout << "  Контраст провалу: " << (res.contrast * 100.0) << "%\n";
        std::cout << "  Кут піка 1: " << res.peak1_deg << "°\n";
        std::cout << "  Кут піка 2: " << res.peak2_deg << "°\n";

    } catch (const std::exception& ex) {
        std::cerr << "Помилка виконання: " << ex.what() << "\n";
        return 1;
    }

    return 0;
}
