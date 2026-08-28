// ParityTestRunner.cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <fstream>
#include <span>
#include "ParityPipeline.hpp"

struct ParityMetrics {
    double cosine_sim{0.0};
    double mae{0.0};
    int max_ae{0};
    double sqnr_db{0.0};
};

ParityMetrics evaluate_parity(std::span<const int8_t> actual, std::span<const int8_t> golden) {
    double dot_prod = 0.0, norm_a = 0.0, norm_g = 0.0, sum_abs_err = 0.0, sum_sig_sq = 0.0, sum_err_sq = 0.0;
    int max_err = 0;

    for (size_t i = 0; i < actual.size(); ++i) {
        const double a = static_cast<double>(actual[i]);
        const double g = static_cast<double>(golden[i]);
        const double err = std::abs(a - g);
        dot_prod += a * g;
        norm_a += a * a;
        norm_g += g * g;
        sum_abs_err += err;
        sum_sig_sq += g * g;
        sum_err_sq += (a - g) * (a - g);
        if (static_cast<int>(err) > max_err) max_err = static_cast<int>(err);
    }

    return {
        .cosine_sim = dot_prod / (std::sqrt(norm_a) * std::sqrt(norm_g) + 1e-12),
        .mae = sum_abs_err / static_cast<double>(actual.size()),
        .max_ae = max_err,
        .sqnr_db = (sum_err_sq > 0.0) ? 10.0 * std::log10(sum_sig_sq / sum_err_sq) : 99.9
    };
}
