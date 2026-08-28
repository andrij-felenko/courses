// tcr_analyzer.cpp - Ідіоматична C++ реалізація з RAII, std::span та std::expected
#include <iostream>
#include <vector>
#include <span>
#include <expected>
#include <cmath>
#include <numeric>

struct TcrMeasurement {
    double temp_c{};
    double v_pos{};  // Напруга при +I, Вольт
    double v_neg{};  // Напруга при -I, Вольт
};

struct TcrFitResult {
    double r0{};       // Опір при 20 °C, Ом
    double alpha_ppm{};// Лінійний ТКО, ppm/K
    double beta_ppm{}; // Квадратичний ТКО, ppm/K^2
    double t_max_c{};  // Температура вершини параболи, °C
};

enum class TcrFitError {
    InsufficientData,
    InvalidCurrent,
    DegenerateMatrix
};

class TcrAnalyzer {
public:
    explicit TcrAnalyzer(double test_current_a) : test_current_(test_current_a) {}

    [[nodiscard]] double compute_true_resistance(const TcrMeasurement& m) const noexcept {
        return ((m.v_pos - m.v_neg) / 2.0) / test_current_;
    }

    [[nodiscard]] double compute_thermal_emf(const TcrMeasurement& m) const noexcept {
        return (m.v_pos + m.v_neg) / 2.0;
    }

    [[nodiscard]] std::expected<TcrFitResult, TcrFitError> 
    fit_parabola(std::span<const TcrMeasurement> data) const noexcept {
        if (data.size() < 3) {
            return std::unexpected(TcrFitError::InsufficientData);
        }
        if (test_current_ <= 0.0) {
            return std::unexpected(TcrFitError::InvalidCurrent);
        }

        double s0 = 0.0, s1 = 0.0, s2 = 0.0, s3 = 0.0, s4 = 0.0;
        double sy = 0.0, s1y = 0.0, s2y = 0.0;

        for (const auto& m : data) {
            double dt = m.temp_c - 20.0;
            double r = compute_true_resistance(m);

            double dt2 = dt * dt;
            s0 += 1.0;
            s1 += dt;
            s2 += dt2;
            s3 += dt * dt2;
            s4 += dt2 * dt2;

            sy += r;
            s1y += dt * r;
            s2y += dt2 * r;
        }

        double det = s0 * (s2 * s4 - s3 * s3) - s1 * (s1 * s4 - s2 * s3) + s2 * (s1 * s3 - s2 * s2);
        if (std::abs(det) < 1e-12) {
            return std::unexpected(TcrFitError::DegenerateMatrix);
        }

        double det_a = sy * (s2 * s4 - s3 * s3) - s1 * (s1y * s4 - s2y * s3) + s2 * (s1y * s3 - s2y * s2);
        double det_b = s0 * (s1y * s4 - s2y * s3) - sy * (s1 * s4 - s2 * s3) + s2 * (s1 * s3 - s2y * s2);
        double det_c = s0 * (s2 * s2y - s1y * s3) - s1 * (s1 * s2y - s1y * s2) + sy * (s1 * s3 - s2 * s2);

        double c0 = det_a / det;
        double c1 = det_b / det;
        double c2 = det_c / det;

        TcrFitResult res{};
        res.r0 = c0;
        res.alpha_ppm = (c1 / c0) * 1e6;
        res.beta_ppm = (c2 / c0) * 1e6;
        res.t_max_c = (std::abs(res.beta_ppm) > 1e-9) 
            ? (20.0 - (res.alpha_ppm / (2.0 * res.beta_ppm))) 
            : 20.0;

        return res;
    }

private:
    double test_current_{1.0};
};
