#include <iostream>
#include <vector>
#include <string>
#include <cmath>
#include <numeric>
#include <span>

struct AnchorEvent {
    std::string name;
    uint64_t t_boot_us;
    uint64_t t_gcs_ms;
};

struct AlignmentModel {
    double alpha_drift;
    double beta_offset_ms;
    double residual_rms_ms;
};

class LogFusionEngine {
public:
    static AlignmentModel calculate_time_warp(std::span<const AnchorEvent> anchors) {
        const size_t p = anchors.size();
        if (p < 2) return {1.0, 0.0, 0.0};

        double sum_tb = 0.0, sum_tg = 0.0;
        for (const auto& a : anchors) {
            sum_tb += static_cast<double>(a.t_boot_us) / 1000.0;
            sum_tg += static_cast<double>(a.t_gcs_ms);
        }

        const double mean_tb = sum_tb / p;
        const double mean_tg = sum_tg / p;

        double cov = 0.0, var_tb = 0.0;
        for (const auto& a : anchors) {
            double tb = (static_cast<double>(a.t_boot_us) / 1000.0) - mean_tb;
            double tg = static_cast<double>(a.t_gcs_ms) - mean_tg;
            cov += tb * tg;
            var_tb += tb * tb;
        }

        const double alpha = (var_tb > 1e-9) ? (cov / var_tb) : 1.0;
        const double beta = mean_tg - alpha * mean_tb;

        double sum_sq = 0.0;
        for (const auto& a : anchors) {
            double tb = static_cast<double>(a.t_boot_us) / 1000.0;
            double diff = static_cast<double>(a.t_gcs_ms) - (alpha * tb + beta);
            sum_sq += diff * diff;
        }

        return {alpha, beta, std::sqrt(sum_sq / p)};
    }
};
