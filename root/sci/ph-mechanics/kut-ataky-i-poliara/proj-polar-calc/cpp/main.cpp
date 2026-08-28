#include <iostream>
#include <vector>
#include <cmath>
#include <optional>
#include <span>
#include <algorithm>
#include <iomanip>

struct PolarPoint {
    double alpha_deg{0.0}; // Кут атаки (градуси)
    double cl{0.0};        // Коефіцієнт підйомної сили
    double cd{0.0};        // Коефіцієнт лобового опору
    double cm{0.0};        // Коефіцієнт поздовжнього моменту (c/4)
};

struct PolarMetrics {
    double alpha_zero_lift_deg{0.0};
    double alpha_crit_deg{0.0};
    double cl_max{-1e9};
    double cd_min{1e9};

    double k_max{-1e9}; // (C_L / C_D)_max — максимальна якість
    double alpha_k_max_deg{0.0};
    double cl_at_k_max{0.0};
    double cd_at_k_max{0.0};

    double e_max{-1e9}; // (C_L^1.5 / C_D)_max — економічний режим
    double alpha_e_max_deg{0.0};

    double j_max{-1e9}; // (C_L^0.5 / C_D)_max — швидкісний режим
    double alpha_j_max_deg{0.0};
};

class AirfoilPolarAnalyzer {
public:
    explicit AirfoilPolarAnalyzer(std::vector<PolarPoint> points, double reynolds_base = 500000.0)
        : points_(std::move(points)), reynolds_base_(reynolds_base) {
        std::ranges::sort(points_, [](const auto& a, const auto& b) {
            return a.alpha_deg < b.alpha_deg;
        });
    }

    [[nodiscard]] std::optional<PolarPoint> evaluate(double alpha_deg) const {
        if (points_.size() < 2 || alpha_deg < points_.front().alpha_deg || alpha_deg > points_.back().alpha_deg) {
            return std::nullopt;
        }

        auto it = std::ranges::lower_bound(points_, alpha_deg, {}, &PolarPoint::alpha_deg);
        if (it == points_.begin()) return *it;

        const auto& p1 = *(it - 1);
        const auto& p2 = *it;
        const double span = p2.alpha_deg - p1.alpha_deg;
        const double t = (span > 1e-9) ? (alpha_deg - p1.alpha_deg) / span : 0.0;

        return PolarPoint{
            .alpha_deg = alpha_deg,
            .cl = p1.cl + t * (p2.cl - p1.cl),
            .cd = p1.cd + t * (p2.cd - p1.cd),
            .cm = p1.cm + t * (p2.cm - p1.cm)
        };
    }

    [[nodiscard]] std::optional<PolarMetrics> analyze() const {
        if (points_.size() < 3) return std::nullopt;

        PolarMetrics metrics{};
        bool found_zero_lift = false;

        for (size_t i = 0; i < points_.size(); ++i) {
            const auto& pt = points_[i];

            if (pt.cl > metrics.cl_max) {
                metrics.cl_max = pt.cl;
                metrics.alpha_crit_deg = pt.alpha_deg;
            }

            if (pt.cd < metrics.cd_min) {
                metrics.cd_min = pt.cd;
            }

            if (i > 0 && !found_zero_lift) {
                const double prev_cl = points_[i - 1].cl;
                if ((prev_cl <= 0.0 && pt.cl >= 0.0) || (prev_cl >= 0.0 && pt.cl <= 0.0)) {
                    const double t = -prev_cl / (pt.cl - prev_cl + 1e-12);
                    metrics.alpha_zero_lift_deg = points_[i - 1].alpha_deg + t * (pt.alpha_deg - points_[i - 1].alpha_deg);
                    found_zero_lift = true;
                }
            }

            if (pt.cl > 0.001 && pt.cd > 0.0001) {
                const double k = pt.cl / pt.cd;
                if (k > metrics.k_max) {
                    metrics.k_max = k;
                    metrics.alpha_k_max_deg = pt.alpha_deg;
                    metrics.cl_at_k_max = pt.cl;
                    metrics.cd_at_k_max = pt.cd;
                }

                const double e = std::pow(pt.cl, 1.5) / pt.cd;
                if (e > metrics.e_max) {
                    metrics.e_max = e;
                    metrics.alpha_e_max_deg = pt.alpha_deg;
                }

                const double j = std::sqrt(pt.cl) / pt.cd;
                if (j > metrics.j_max) {
                    metrics.j_max = j;
                    metrics.alpha_j_max_deg = pt.alpha_deg;
                }
            }
        }
        return metrics;
    }

    [[nodiscard]] static std::optional<double> centerOfPressure(double cl, double cm_c4) noexcept {
        if (std::abs(cl) < 0.02) {
            return std::nullopt; // Близько до нульової підйомної сили — центр тиску невизначений
        }
        return 0.25 - (cm_c4 / cl);
    }

    [[nodiscard]] double scaleForReynolds(double cd_base, double re_target) const noexcept {
        if (re_target <= 1000.0 || reynolds_base_ <= 1000.0) return cd_base;

        const double scale = std::pow(reynolds_base_ / re_target, 0.20);
        double cd_scaled = cd_base * scale;

        if (re_target < 100000.0) {
            const double lsb_factor = (100000.0 - re_target) / 100000.0;
            cd_scaled += 0.015 * lsb_factor * lsb_factor; // Додатковий опір LSB
        }
        return cd_scaled;
    }

private:
    std::vector<PolarPoint> points_;
    double reynolds_base_{500000.0};
};
