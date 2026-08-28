#include <array>
#include <cmath>
#include <numbers>
#include <span>
#include <cstdint>

class MagCalibrator {
public:
    static constexpr size_t kAzimuthSectors = 12;
    static constexpr size_t kElevationSectors = 6;
    static constexpr size_t kTotalBins = kAzimuthSectors * kElevationSectors;
    static constexpr size_t kMinSamples = 36;
    static constexpr uint8_t kMaxPerBin = 5;

    struct Vec3 {
        float x{0.0f}, y{0.0f}, z{0.0f};
    };

    struct Matrix3x3 {
        std::array<std::array<float, 3>, 3> m{{{1,0,0}, {0,1,0}, {0,0,1}}};
    };

    explicit MagCalibrator(float earth_field_uT = 45.0f) noexcept
        : earth_field_uT_{earth_field_uT > 10.0f ? earth_field_uT : 45.0f} {
        reset();
    }

    void reset() noexcept {
        for (auto& row : hth_) row.fill(0.0f);
        ht1_.fill(0.0f);
        bin_counts_.fill(0);
        total_samples_ = 0;
        is_calibrated_ = false;
        v_hard_ = {};
        t_soft_ = Matrix3x3{};
    }

    bool add_sample(const Vec3& sample) noexcept {
        const size_t bin = compute_bin_index(sample);
        if (bin_counts_[bin] >= kMaxPerBin) {
            return false;
        }

        bin_counts_[bin]++;
        total_samples_++;

        const std::array<float, 9> h{
            sample.x * sample.x,
            sample.y * sample.y,
            sample.z * sample.z,
            sample.x * sample.y,
            sample.x * sample.z,
            sample.y * sample.z,
            sample.x,
            sample.y,
            sample.z
        };

        for (size_t i = 0; i < 9; ++i) {
            ht1_[i] += h[i];
            for (size_t j = 0; j < 9; ++j) {
                hth_[i][j] += h[i] * h[j];
            }
        }
        return true;
    }

    bool compute() noexcept {
        if (total_samples_ < kMinSamples) return false;

        std::array<float, 9> p{};
        if (!solve_linear_system_9x9(hth_, ht1_, p)) return false;

        Matrix3x3 A{{{
            { p[0],        p[3] * 0.5f, p[4] * 0.5f },
            { p[3] * 0.5f, p[1],        p[5] * 0.5f },
            { p[4] * 0.5f, p[5] * 0.5f, p[2]        }
        }}};
        const Vec3 b{ p[6] * 0.5f, p[7] * 0.5f, p[8] * 0.5f };

        Matrix3x3 A_inv{};
        if (!invert_matrix_3x3(A, A_inv)) return false;

        v_hard_.x = -(A_inv.m[0][0] * b.x + A_inv.m[0][1] * b.y + A_inv.m[0][2] * b.z);
        v_hard_.y = -(A_inv.m[1][0] * b.x + A_inv.m[1][1] * b.y + A_inv.m[1][2] * b.z);
        v_hard_.z = -(A_inv.m[2][0] * b.x + A_inv.m[2][1] * b.y + A_inv.m[2][2] * b.z);

        const Vec3 Av{
            A.m[0][0] * v_hard_.x + A.m[0][1] * v_hard_.y + A.m[0][2] * v_hard_.z,
            A.m[1][0] * v_hard_.x + A.m[1][1] * v_hard_.y + A.m[1][2] * v_hard_.z,
            A.m[2][0] * v_hard_.x + A.m[2][1] * v_hard_.y + A.m[2][2] * v_hard_.z
        };
        const float scale = v_hard_.x * Av.x + v_hard_.y * Av.y + v_hard_.z * Av.z + 1.0f;
        if (scale <= 1e-6f) return false;

        Matrix3x3 M{};
        for (size_t i = 0; i < 3; ++i) {
            for (size_t j = 0; j < 3; ++j) {
                M.m[i][j] = A.m[i][j] / scale;
            }
        }

        Matrix3x3 L{};
        if (M.m[0][0] <= 0.0f) return false;
        L.m[0][0] = std::sqrt(M.m[0][0]);
        L.m[1][0] = M.m[1][0] / L.m[0][0];
        L.m[2][0] = M.m[2][0] / L.m[0][0];

        const float d11 = M.m[1][1] - L.m[1][0] * L.m[1][0];
        if (d11 <= 0.0f) return false;
        L.m[1][1] = std::sqrt(d11);
        L.m[2][1] = (M.m[2][1] - L.m[2][0] * L.m[1][0]) / L.m[1][1];

        const float d22 = M.m[2][2] - L.m[2][0] * L.m[2][0] - L.m[2][1] * L.m[2][1];
        if (d22 <= 0.0f) return false;
        L.m[2][2] = std::sqrt(d22);

        for (size_t i = 0; i < 3; ++i) {
            for (size_t j = 0; j < 3; ++j) {
                t_soft_.m[i][j] = earth_field_uT_ * L.m[j][i];
            }
        }

        is_calibrated_ = true;
        return true;
    }

    [[nodiscard]] Vec3 apply(const Vec3& raw) const noexcept {
        if (!is_calibrated_) return raw;
        const float dx = raw.x - v_hard_.x;
        const float dy = raw.y - v_hard_.y;
        const float dz = raw.z - v_hard_.z;

        return Vec3{
            t_soft_.m[0][0] * dx + t_soft_.m[0][1] * dy + t_soft_.m[0][2] * dz,
            t_soft_.m[1][0] * dx + t_soft_.m[1][1] * dy + t_soft_.m[1][2] * dz,
            t_soft_.m[2][0] * dx + t_soft_.m[2][1] * dy + t_soft_.m[2][2] * dz
        };
    }

    [[nodiscard]] bool is_calibrated() const noexcept { return is_calibrated_; }
    [[nodiscard]] const Vec3& hard_iron_offset() const noexcept { return v_hard_; }
    [[nodiscard]] const Matrix3x3& soft_iron_matrix() const noexcept { return t_soft_; }

private:
    float earth_field_uT_{45.0f};
    std::array<std::array<float, 9>, 9> hth_{};
    std::array<float, 9> ht1_{};
    std::array<uint8_t, kTotalBins> bin_counts_{};
    uint32_t total_samples_{0};
    bool is_calibrated_{false};
    Vec3 v_hard_{};
    Matrix3x3 t_soft_{};

    static size_t compute_bin_index(const Vec3& p) noexcept {
        const float norm = std::sqrt(p.x * p.x + p.y * p.y + p.z * p.z);
        if (norm < 1e-4f) return 0;

        float azimuth = std::atan2(p.y, p.x);
        if (azimuth < 0.0f) azimuth += 2.0f * std::numbers::pi_v<float>;
        auto az_bin = static_cast<size_t>(azimuth / (2.0f * std::numbers::pi_v<float> / kAzimuthSectors));
        if (az_bin >= kAzimuthSectors) az_bin = kAzimuthSectors - 1;

        const float elevation = std::asin(p.z / norm);
        const float norm_elev = elevation + std::numbers::pi_v<float> * 0.5f;
        auto el_bin = static_cast<size_t>(norm_elev / (std::numbers::pi_v<float> / kElevationSectors));
        if (el_bin >= kElevationSectors) el_bin = kElevationSectors - 1;

        return el_bin * kAzimuthSectors + az_bin;
    }

    static bool solve_linear_system_9x9(
        const std::array<std::array<float, 9>, 9>& A,
        const std::array<float, 9>& b,
        std::array<float, 9>& x_out) noexcept {
        std::array<std::array<float, 10>, 9> M{};
        for (size_t i = 0; i < 9; ++i) {
            for (size_t j = 0; j < 9; ++j) M[i][j] = A[i][j];
            M[i][9] = b[i];
        }

        for (size_t col = 0; col < 9; ++col) {
            size_t max_row = col;
            float max_val = std::abs(M[col][col]);
            for (size_t row = col + 1; row < 9; ++row) {
                if (const float v = std::abs(M[row][col]); v > max_val) {
                    max_val = v;
                    max_row = row;
                }
            }
            if (max_val < 1e-9f) return false;

            if (max_row != col) {
                std::swap(M[col], M[max_row]);
            }

            for (size_t row = col + 1; row < 9; ++row) {
                const float factor = M[row][col] / M[col][col];
                for (size_t k = col; k < 10; ++k) {
                    M[row][k] -= factor * M[col][k];
                }
            }
        }

        for (int row = 8; row >= 0; --row) {
            float sum = M[static_cast<size_t>(row)][9];
            for (size_t col = static_cast<size_t>(row) + 1; col < 9; ++col) {
                sum -= M[static_cast<size_t>(row)][col] * x_out[col];
            }
            x_out[static_cast<size_t>(row)] = sum / M[static_cast<size_t>(row)][static_cast<size_t>(row)];
        }
        return true;
    }

    static bool invert_matrix_3x3(const Matrix3x3& A, Matrix3x3& inv) noexcept {
        const float det = A.m[0][0] * (A.m[1][1] * A.m[2][2] - A.m[1][2] * A.m[2][1]) -
                          A.m[0][1] * (A.m[1][0] * A.m[2][2] - A.m[1][2] * A.m[2][0]) +
                          A.m[0][2] * (A.m[1][0] * A.m[2][1] - A.m[1][1] * A.m[2][0]);
        if (std::abs(det) < 1e-12f) return false;

        const float inv_det = 1.0f / det;
        inv.m[0][0] = (A.m[1][1] * A.m[2][2] - A.m[1][2] * A.m[2][1]) * inv_det;
        inv.m[0][1] = (A.m[0][2] * A.m[2][1] - A.m[0][1] * A.m[2][2]) * inv_det;
        inv.m[0][2] = (A.m[0][1] * A.m[1][2] - A.m[0][2] * A.m[1][1]) * inv_det;
        inv.m[1][0] = (A.m[1][2] * A.m[2][0] - A.m[1][0] * A.m[2][2]) * inv_det;
        inv.m[1][1] = (A.m[0][0] * A.m[2][2] - A.m[0][2] * A.m[2][0]) * inv_det;
        inv.m[1][2] = (A.m[0][2] * A.m[1][0] - A.m[0][0] * A.m[1][2]) * inv_det;
        inv.m[2][0] = (A.m[1][0] * A.m[2][1] - A.m[1][1] * A.m[2][0]) * inv_det;
        inv.m[2][1] = (A.m[0][1] * A.m[2][0] - A.m[0][0] * A.m[2][1]) * inv_det;
        inv.m[2][2] = (A.m[0][0] * A.m[1][1] - A.m[0][1] * A.m[1][0]) * inv_det;
        return true;
    }
};
