/* ==========================================================================
 *  mag_cal_pipeline.hpp — Ідіоматичний модульний C++ калібратор магнітометра
 * ========================================================================== */

#pragma once

#include <array>
#include <cmath>
#include <cstdint>
#include <optional>
#include <span>
#include <algorithm>

namespace drone::sensors {

struct Vector3f {
    float x{0.0f}, y{0.0f}, z{0.0f};

    [[nodiscard]] constexpr Vector3f operator-(const Vector3f& rhs) const noexcept {
        return { x - rhs.x, y - rhs.y, z - rhs.z };
    }
    [[nodiscard]] constexpr Vector3f operator+(const Vector3f& rhs) const noexcept {
        return { x + rhs.x, y + rhs.y, z + rhs.z };
    }
    [[nodiscard]] constexpr float dot(const Vector3f& rhs) const noexcept {
        return x * rhs.x + y * rhs.y + z * rhs.z;
    }
    [[nodiscard]] float norm() const noexcept {
        return std::sqrt(dot(*this));
    }
};

struct Matrix3f {
    std::array<std::array<float, 3>, 3> m{{{1,0,0}, {0,1,0}, {0,0,1}}};

    [[nodiscard]] constexpr Vector3f operator*(const Vector3f& v) const noexcept {
        return {
            m[0][0] * v.x + m[0][1] * v.y + m[0][2] * v.z,
            m[1][0] * v.x + m[1][1] * v.y + m[1][2] * v.z,
            m[2][0] * v.x + m[2][1] * v.y + m[2][2] * v.z
        };
    }

    [[nodiscard]] float condition_number() const noexcept {
        const float trace = std::abs(m[0][0]) + std::abs(m[1][1]) + std::abs(m[2][2]);
        const float min_diag = std::min({std::abs(m[0][0]), std::abs(m[1][1]), std::abs(m[2][2])});
        if (min_diag < 1e-4f) return 999.0f;
        return (trace / 3.0f) / min_diag;
    }
};

struct CalibrationResult {
    Vector3f offset{};          // Hard Iron V_0
    Matrix3f soft_iron{};       // Soft Iron W
    float    earth_field{45.0f};
    float    rms_residual{0.0f};
    float    coverage_pct{0.0f};
    float    condition_num{1.0f};
    bool     valid{false};

    [[nodiscard]] Vector3f apply(const Vector3f& raw) const noexcept {
        if (!valid) return raw;
        return soft_iron * (raw - offset);
    }
};

template <size_t LatBins = 6, size_t LonBins = 12, size_t SamplesPerBin = 4>
class SpatialMagCollector {
public:
    static constexpr size_t TotalBins = LatBins * LonBins;
    static constexpr size_t MaxSamples = TotalBins * SamplesPerBin;

    explicit SpatialMagCollector(float target_earth_field = 45.0f) noexcept
        : target_earth_field_{target_earth_field} {}

    void reset() noexcept {
        sample_counts_.fill(0);
        total_points_ = 0;
    }

    bool push(const Vector3f& raw, const Vector3f& gyro_rad_s) noexcept {
        if (gyro_rad_s.norm() > 1.745f) { // > 100 deg/s
            return false;
        }

        const auto bin_idx = calculate_bin(raw);
        if (!bin_idx) return false;

        auto& count = sample_counts_[*bin_idx];
        if (count < SamplesPerBin) {
            samples_[*bin_idx][count] = raw;
            ++count;
            ++total_points_;
            return true;
        }
        return false;
    }

    [[nodiscard]] float coverage_percentage() const noexcept {
        size_t filled = 0;
        for (auto count : sample_counts_) {
            if (count > 0) ++filled;
        }
        return (static_cast<float>(filled) / static_cast<float>(TotalBins)) * 100.0f;
    }

    [[nodiscard]] std::optional<CalibrationResult> solve() const noexcept {
        const float coverage = coverage_percentage();
        if (coverage < 60.0f || total_points_ < 40) {
            return std::nullopt;
        }

        std::array<float, 9> p{0, 0, 0, 1.0f, 0, 0, 1.0f, 0, 1.0f};
        
        // Початковий центр як вибіркове середнє
        Vector3f sum{};
        for (size_t b = 0; b < TotalBins; ++b) {
            for (size_t s = 0; s < sample_counts_[b]; ++s) {
                sum = sum + samples_[b][s];
            }
        }
        p[0] = sum.x / static_cast<float>(total_points_);
        p[1] = sum.y / static_cast<float>(total_points_);
        p[2] = sum.z / static_cast<float>(total_points_);

        float lambda = 1.0f;

        for (size_t iter = 0; iter < 20; ++iter) {
            std::array<std::array<float, 9>, 9> H{};
            std::array<float, 9> g{};

            Matrix3f W{{{
                { p[3], p[4], p[5] },
                { p[4], p[6], p[7] },
                { p[5], p[7], p[8] }
            }}};
            Vector3f V0{ p[0], p[1], p[2] };

            for (size_t b = 0; b < TotalBins; ++b) {
                for (size_t s = 0; s < sample_counts_[b]; ++s) {
                    const Vector3f raw = samples_[b][s];
                    const Vector3f d = raw - V0;
                    const Vector3f cal = W * d;
                    const float cal_norm = std::max(cal.norm(), 1e-4f);
                    const float r = cal_norm - target_earth_field_;

                    const Vector3f u{ cal.x / cal_norm, cal.y / cal_norm, cal.z / cal_norm };

                    std::array<float, 9> J{
                        -(u.x * W.m[0][0] + u.y * W.m[1][0] + u.z * W.m[2][0]),
                        -(u.x * W.m[0][1] + u.y * W.m[1][1] + u.z * W.m[2][1]),
                        -(u.x * W.m[0][2] + u.y * W.m[1][2] + u.z * W.m[2][2]),
                        u.x * d.x,
                        u.x * d.y + u.y * d.x,
                        u.x * d.z + u.z * d.x,
                        u.y * d.y,
                        u.y * d.z + u.z * d.y,
                        u.z * d.z
                    };

                    for (size_t j = 0; j < 9; ++j) {
                        g[j] += J[j] * r;
                        for (size_t k = 0; k < 9; ++k) {
                            H[j][k] += J[j] * J[k];
                        }
                    }
                }
            }

            for (size_t i = 0; i < 9; ++i) {
                H[i][i] += lambda * (H[i][i] + 1e-3f);
            }

            // Гаусове розв'язання H * dp = -g
            std::array<float, 9> dp{};
            for (size_t i = 0; i < 9; ++i) dp[i] = -g[i];

            bool singular = false;
            for (size_t i = 0; i < 9; ++i) {
                size_t max_r = i;
                float max_val = std::abs(H[i][i]);
                for (size_t k = i + 1; k < 9; ++k) {
                    if (std::abs(H[k][i]) > max_val) {
                        max_val = std::abs(H[k][i]);
                        max_r = k;
                    }
                }
                if (max_val < 1e-8f) { singular = true; break; }

                if (max_r != i) {
                    std::swap(H[i], H[max_r]);
                    std::swap(dp[i], dp[max_r]);
                }

                for (size_t k = i + 1; k < 9; ++k) {
                    float factor = H[k][i] / H[i][i];
                    for (size_t j = i; j < 9; j++) {
                        H[k][j] -= factor * H[i][j];
                    }
                    dp[k] -= factor * dp[i];
                }
            }

            if (singular) {
                lambda *= 10.0f;
                continue;
            }

            for (int i = 8; i >= 0; --i) {
                for (size_t j = i + 1; j < 9; ++j) {
                    dp[i] -= H[i][j] * dp[j];
                }
                dp[i] /= H[i][i];
            }

            float step_norm_sq = 0.0f;
            for (size_t i = 0; i < 9; ++i) {
                p[i] += dp[i];
                step_norm_sq += dp[i] * dp[i];
            }

            if (std::sqrt(step_norm_sq) < 1e-4f) break;
            lambda = std::max(lambda * 0.2f, 1e-6f);
        }

        CalibrationResult res{};
        res.offset = { p[0], p[1], p[2] };
        res.soft_iron = Matrix3f{{{
            { p[3], p[4], p[5] },
            { p[4], p[6], p[7] },
            { p[5], p[7], p[8] }
        }}};
        res.earth_field = target_earth_field_;
        res.coverage_pct = coverage;
        res.condition_num = res.soft_iron.condition_number();

        float sum_sq = 0.0f;
        for (size_t b = 0; b < TotalBins; ++b) {
            for (size_t s = 0; s < sample_counts_[b]; ++s) {
                const auto cal = res.apply(samples_[b][s]);
                const float err = cal.norm() - target_earth_field_;
                sum_sq += err * err;
            }
        }
        res.rms_residual = std::sqrt(sum_sq / static_cast<float>(total_points_));
        res.valid = (res.rms_residual < 3.0f) && (res.condition_num < 2.5f);

        return res;
    }

private:
    [[nodiscard]] std::optional<size_t> calculate_bin(const Vector3f& raw) const noexcept {
        const float norm = raw.norm();
        if (norm < 1e-3f) return std::nullopt;

        const float elev = std::asin(std::clamp(raw.z / norm, -1.0f, 1.0f));
        const float azim = std::atan2(raw.y, raw.x);

        int lat_idx = static_cast<int>((elev + 1.5707963f) / (3.1415926f / LatBins));
        lat_idx = std::clamp(lat_idx, 0, static_cast<int>(LatBins - 1));

        int lon_idx = static_cast<int>((azim + 3.1415926f) / (6.2831853f / LonBins));
        lon_idx = std::clamp(lon_idx, 0, static_cast<int>(LonBins - 1));

        return static_cast<size_t>(lat_idx * LonBins + lon_idx);
    }

    std::array<std::array<Vector3f, SamplesPerBin>, TotalBins> samples_{};
    std::array<uint8_t, TotalBins> sample_counts_{};
    size_t total_points_{0};
    float target_earth_field_{45.0f};
};

} // namespace drone::sensors
