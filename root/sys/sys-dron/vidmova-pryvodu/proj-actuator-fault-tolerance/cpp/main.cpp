#include <array>
#include <cmath>
#include <cstdint>
#include <span>
#include <algorithm>
#include <optional>

class DynamicMixerAllocator {
public:
    static constexpr size_t kMaxActuators = 8;
    static constexpr size_t kAxes = 4; // 0: Thrust, 1: Roll, 2: Pitch, 3: Yaw
    static constexpr float kTikhonovDamping = 0.0001f;

    DynamicMixerAllocator(size_t num_actuators,
                          const std::array<std::array<float, kMaxActuators>, kAxes>& b_matrix,
                          float slew_rate = 20.0f)
        : num_actuators_(std::min(num_actuators, kMaxActuators)),
          b_matrix_(b_matrix),
          slew_rate_max_(slew_rate > 0.0f ? slew_rate : 20.0f) {
        weights_.fill(1.0f);
        u_min_.fill(0.0f);
        u_max_.fill(1.0f);
        u_prev_.fill(0.0f);
        recompute_pinv();
    }

    void set_fault_mask(uint8_t mask, bool relax_yaw) noexcept {
        if (fault_mask_ != mask || is_yaw_relaxed_ != relax_yaw) {
            fault_mask_ = mask;
            is_yaw_relaxed_ = relax_yaw;
            recompute_pinv();
        }
    }

    void allocate(std::span<const float, kAxes> tau_des,
                  float dt,
                  std::span<float> u_out) noexcept {
        const std::array<float, kAxes> tau{
            tau_des[0],
            tau_des[1],
            tau_des[2],
            is_yaw_relaxed_ ? 0.0f : tau_des[3]
        };

        const float max_slew = slew_rate_max_ * dt;
        const size_t limit = std::min(u_out.size(), num_actuators_);

        for (size_t i = 0; i < limit; ++i) {
            if (fault_mask_ & (1U << i)) {
                u_out[i] = 0.0f;
                u_prev_[i] = 0.0f;
                continue;
            }

            float cmd = 0.0f;
            for (size_t ax = 0; ax < kAxes; ++ax) {
                cmd += b_pinv_[i][ax] * tau[ax];
            }

            float clamped = std::clamp(cmd, u_min_[i], u_max_[i]);

            if (dt > 0.0001f) {
                const float delta = clamped - u_prev_[i];
                if (delta > max_slew) clamped = u_prev_[i] + max_slew;
                if (delta < -max_slew) clamped = u_prev_[i] - max_slew;
            }

            u_out[i] = clamped;
            u_prev_[i] = clamped;
        }
    }

    [[nodiscard]] uint8_t fault_mask() const noexcept { return fault_mask_; }
    [[nodiscard]] bool is_yaw_relaxed() const noexcept { return is_yaw_relaxed_; }

private:
    bool recompute_pinv() noexcept {
        // 1. Формування матриці Грама G = B * W⁻¹ * Bᵀ
        std::array<std::array<float, kAxes>, kAxes> g{};

        for (size_t ax1 = 0; ax1 < kAxes; ++ax1) {
            for (size_t ax2 = 0; ax2 < kAxes; ++ax2) {
                float sum = 0.0f;
                for (size_t i = 0; i < num_actuators_; ++i) {
                    if (!(fault_mask_ & (1U << i))) {
                        const float inv_w = 1.0f / weights_[i];
                        sum += b_matrix_[ax1][i] * inv_w * b_matrix_[ax2][i];
                    }
                }
                g[ax1][ax2] = sum;
            }
        }

        if (is_yaw_relaxed_) {
            g[3][0] = 0.0f; g[3][1] = 0.0f; g[3][2] = 0.0f;
            g[0][3] = 0.0f; g[1][3] = 0.0f; g[2][3] = 0.0f;
            g[3][3] = 1.0f;
        }

        for (size_t ax = 0; ax < kAxes; ++ax) {
            g[ax][ax] += kTikhonovDamping;
        }

        // 2. Обернення матриці 4x4
        auto g_inv_opt = invert_4x4(g);
        if (!g_inv_opt) return false;
        const auto& g_inv = *g_inv_opt;

        // 3. B_pinv = W⁻¹ * Bᵀ * G⁻¹
        for (size_t i = 0; i < num_actuators_; ++i) {
            if (fault_mask_ & (1U << i)) {
                b_pinv_[i].fill(0.0f);
            } else {
                const float inv_w = 1.0f / weights_[i];
                for (size_t ax = 0; ax < kAxes; ++ax) {
                    float sum = 0.0f;
                    for (size_t k = 0; k < kAxes; ++k) {
                        sum += b_matrix_[k][i] * g_inv[k][ax];
                    }
                    b_pinv_[i][ax] = inv_w * sum;
                }
            }
        }
        return true;
    }

    static std::optional<std::array<std::array<float, kAxes>, kAxes>>
    invert_4x4(const std::array<std::array<float, kAxes>, kAxes>& a) noexcept {
        std::array<std::array<float, 8>, 4> m{};
        for (size_t i = 0; i < 4; ++i) {
            for (size_t j = 0; j < 4; ++j) m[i][j] = a[i][j];
            for (size_t j = 4; j < 8; ++j) m[i][j] = (i == (j - 4)) ? 1.0f : 0.0f;
        }

        for (size_t i = 0; i < 4; ++i) {
            size_t pivot = i;
            float max_val = std::abs(m[i][i]);
            for (size_t k = i + 1; k < 4; ++k) {
                if (std::abs(m[k][i]) > max_val) {
                    max_val = std::abs(m[k][i]);
                    pivot = k;
                }
            }
            if (max_val < 1e-7f) return std::nullopt;

            if (pivot != i) {
                std::swap(m[i], m[pivot]);
            }

            const float pivot_val = m[i][i];
            for (size_t j = 0; j < 8; ++j) m[i][j] /= pivot_val;

            for (size_t k = 0; k < 4; ++k) {
                if (k != i) {
                    const float factor = m[k][i];
                    for (size_t j = 0; j < 8; ++j) {
                        m[k][j] -= factor * m[i][j];
                    }
                }
            }
        }

        std::array<std::array<float, kAxes>, kAxes> inv{};
        for (size_t i = 0; i < 4; ++i) {
            for (size_t j = 0; j < 4; ++j) {
                inv[i][j] = m[i][j + 4];
            }
        }
        return inv;
    }

    size_t num_actuators_{0};
    std::array<std::array<float, kMaxActuators>, kAxes> b_matrix_{};
    std::array<std::array<float, kAxes>, kMaxActuators> b_pinv_{};
    std::array<float, kMaxActuators> weights_{};
    std::array<float, kMaxActuators> u_min_{};
    std::array<float, kMaxActuators> u_max_{};
    std::array<float, kMaxActuators> u_prev_{};
    float slew_rate_max_{20.0f};
    uint8_t fault_mask_{0};
    bool is_yaw_relaxed_{false};
};
