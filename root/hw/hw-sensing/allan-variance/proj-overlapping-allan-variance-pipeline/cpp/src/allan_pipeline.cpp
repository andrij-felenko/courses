#include "allan_pipeline.hpp"
#include <algorithm>
#include <numeric>
#include <stdexcept>

namespace sensing {

AllanVariancePipeline::AllanVariancePipeline(Span<const double> rate_data, double dt)
    : m_dt(dt), m_samples(rate_data.size())
{
    if (m_samples == 0 || m_dt <= 0.0) {
        throw std::invalid_argument("Некоректний розмір вибірки або крок часу");
    }

    // 1. Обчислення масиву інтегральних префіксних сум за O(N)
    m_phase.resize(m_samples + 1, 0.0);
    for (size_t i = 0; i < m_samples; ++i) {
        m_phase[i + 1] = m_phase[i] + rate_data[i] * m_dt;
    }
}

double AllanVariancePipeline::approx_edf(size_t n, size_t m, NoiseType noise) {
    if (m == 0 || n <= 2 * m) return 1.0;
    const double N = static_cast<double>(n);
    const double M = static_cast<double>(m);
    double edf = 1.0;

    switch (noise) {
        case NoiseType::WFM:
            edf = (3.0 * (N - 1.0) / (2.0 * M)) - (2.0 * (N - 2.0) / N);
            break;
        case NoiseType::FFM:
            edf = (2.0 * (N - 2.0) * (N - 2.0)) / (M * (3.0 * N - 5.0));
            break;
        case NoiseType::RWFM:
            edf = (N - 1.0) / M;
            break;
    }
    return std::max(1.0, edf);
}

void AllanVariancePipeline::calc_confidence_interval(
    double adev, double edf, double& ci_min, double& ci_max)
{
    const double v = std::max(1.0, edf);
    const double z = 1.95996; // 95% двосторонній довірчий рівень

    // Апроксимація квантилів Вілсона — Гілферті
    auto chi2_q = [v](double sign_z) {
        double factor = 1.0 - (2.0 / (9.0 * v)) + sign_z * std::sqrt(2.0 / (9.0 * v));
        factor = std::max(0.001, factor);
        return v * factor * factor * factor;
    };

    const double chi2_low = std::max(1e-9, chi2_q(-z));
    const double chi2_high = std::max(1e-9, chi2_q(z));

    ci_min = adev * std::sqrt(v / chi2_high);
    ci_max = adev * std::sqrt(v / chi2_low);
}

std::vector<AllanPoint> AllanVariancePipeline::compute_oavar(
    const std::vector<size_t>& cluster_multipliers,
    NoiseType noise) const
{
    std::vector<AllanPoint> results;
    results.reserve(cluster_multipliers.size());

    for (size_t m : cluster_multipliers) {
        if (m == 0 || m_phase.size() < 2 * m + 1) continue;

        const size_t num_pairs = m_phase.size() - 2 * m - 1;
        if (num_pairs == 0) continue;

        double sum_diff2 = 0.0;
        for (size_t i = 0; i < num_pairs; ++i) {
            const double d2 = m_phase[i + 2 * m] - 2.0 * m_phase[i + m] + m_phase[i];
            sum_diff2 += d2 * d2;
        }

        const double tau = static_cast<double>(m) * m_dt;
        const double avar = sum_diff2 / (2.0 * static_cast<double>(num_pairs) * tau * tau);
        const double adev = std::sqrt(std::max(0.0, avar));
        const double edf = approx_edf(m_samples, m, noise);

        AllanPoint pt;
        pt.tau = tau;
        pt.adev = adev;
        pt.edf = edf;
        pt.num_pairs = num_pairs;
        calc_confidence_interval(adev, edf, pt.adev_min, pt.adev_max);

        results.push_back(pt);
    }
    return results;
}

std::vector<AllanPoint> AllanVariancePipeline::compute_mvar(
    const std::vector<size_t>& cluster_multipliers,
    NoiseType noise) const
{
    std::vector<AllanPoint> results;
    results.reserve(cluster_multipliers.size());

    for (size_t m : cluster_multipliers) {
        if (m == 0 || m_phase.size() < 3 * m) continue;

        const size_t num_terms = m_phase.size() - 3 * m;
        if (num_terms == 0) continue;

        double sum_diff2 = 0.0;
        for (size_t i = 0; i < num_terms; ++i) {
            double inner_sum = 0.0;
            for (size_t j = 0; j < m; ++j) {
                inner_sum += (m_phase[i + j + 2 * m] - 2.0 * m_phase[i + j + m] + m_phase[i + j]);
            }
            sum_diff2 += inner_sum * inner_sum;
        }

        const double tau = static_cast<double>(m) * m_dt;
        const double m_sq = static_cast<double>(m * m);
        const double mvar = sum_diff2 / (2.0 * static_cast<double>(num_terms) * m_sq * tau * tau);
        const double mdev = std::sqrt(std::max(0.0, mvar));
        const double edf = approx_edf(m_samples, m, noise);

        AllanPoint pt;
        pt.tau = tau;
        pt.adev = mdev;
        pt.edf = edf;
        pt.num_pairs = num_terms;
        calc_confidence_interval(mdev, edf, pt.adev_min, pt.adev_max);

        results.push_back(pt);
    }
    return results;
}

} // namespace sensing
