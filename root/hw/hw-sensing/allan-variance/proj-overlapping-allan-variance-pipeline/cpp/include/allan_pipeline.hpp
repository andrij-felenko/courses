#pragma once

#include <vector>
#include <cstddef>
#include <cmath>

#if __has_include(<span>)
#include <span>
template<typename T>
using Span = std::span<T>;
#else
template<typename T>
class Span {
    const T* m_ptr;
    size_t m_size;
public:
    Span(const std::vector<T>& v) : m_ptr(v.data()), m_size(v.size()) {}
    Span(const T* ptr, size_t size) : m_ptr(ptr), m_size(size) {}
    const T* data() const { return m_ptr; }
    size_t size() const { return m_size; }
    const T& operator[](size_t idx) const { return m_ptr[idx]; }
};
#endif

namespace sensing {

enum class NoiseType {
    WFM = 0,  // Білий шум частоти / Angle Random Walk (ARW)
    FFM,      // Флікер-шум частоти / Bias Instability (BI)
    RWFM      // Випадкове блукання частоти / Rate Random Walk (RRW)
};

struct AllanPoint {
    double tau{0.0};
    double adev{0.0};
    double adev_min{0.0};
    double adev_max{0.0};
    double edf{0.0};
    size_t num_pairs{0};
};

class AllanVariancePipeline {
public:
    AllanVariancePipeline(Span<const double> rate_data, double dt);

    std::vector<AllanPoint> compute_oavar(
        const std::vector<size_t>& cluster_multipliers,
        NoiseType noise = NoiseType::WFM
    ) const;

    std::vector<AllanPoint> compute_mvar(
        const std::vector<size_t>& cluster_multipliers,
        NoiseType noise = NoiseType::WFM
    ) const;

    static double approx_edf(size_t n, size_t m, NoiseType noise);
    static void calc_confidence_interval(double adev, double edf, double& ci_min, double& ci_max);

private:
    std::vector<double> m_phase; // Префіксні суми фази: x[k]
    double m_dt{0.01};
    size_t m_samples{0};
};

} // namespace sensing
