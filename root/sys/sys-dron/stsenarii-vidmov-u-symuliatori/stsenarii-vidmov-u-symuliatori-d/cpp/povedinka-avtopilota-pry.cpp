#include <array>
#include <chrono>
#include <cmath>
#include <optional>

struct Vector3f {
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};

    constexpr Vector3f operator-(const Vector3f& rhs) const noexcept {
        return { x - rhs.x, y - rhs.y, z - rhs.z };
    }
};

class EkfGateChecker {
public:
    static constexpr float kChi2Threshold3D = 11.34f;
    static constexpr auto kDefaultTimeout = std::chrono::milliseconds(1500);

    explicit EkfGateChecker(std::chrono::microseconds timeout = kDefaultTimeout)
        : timeout_duration_(timeout) {}

    [[nodiscard]] bool check_innovation(const Vector3f& z_meas,
                                       const Vector3f& pred_state,
                                       const std::array<std::array<float, 3>, 3>& cov_s,
                                       std::chrono::microseconds now) noexcept {
        const Vector3f innov = z_meas - pred_state;
        const auto inv_s = invert_3x3(cov_s);

        if (!inv_s) {
            gate_passed_ = false;
            update_timeout(now);
            return false;
        }

        const std::array<float, 3> y = { innov.x, innov.y, innov.z };
        std::array<float, 3> temp = { 0.0f, 0.0f, 0.0f };

        for (size_t i = 0; i < 3; ++i) {
            for (size_t j = 0; j < 3; ++j) {
                temp[i] += y[j] * (*inv_s)[j][i];
            }
        }

        const float nis = temp[0]*y[0] + temp[1]*y[1] + temp[2]*y[2];

        if (nis <= kChi2Threshold3D) {
            gate_passed_ = true;
            last_valid_time_ = now;
            navigation_lost_ = false;
            return true;
        }

        gate_passed_ = false;
        update_timeout(now);
        return false;
    }

    [[nodiscard]] bool is_navigation_lost() const noexcept { return navigation_lost_; }
    [[nodiscard]] bool is_gate_passed() const noexcept { return gate_passed_; }

private:
    void update_timeout(std::chrono::microseconds now) noexcept {
        if (now - last_valid_time_ > timeout_duration_) {
            navigation_lost_ = true;
        }
    }

    static std::optional<std::array<std::array<float, 3>, 3>> invert_3x3(
        const std::array<std::array<float, 3>, 3>& m) noexcept {
        const float det = m[0][0]*(m[1][1]*m[2][2] - m[1][2]*m[2][1]) -
                          m[0][1]*(m[1][0]*m[2][2] - m[1][2]*m[2][0]) +
                          m[0][2]*(m[1][0]*m[2][1] - m[1][2]*m[2][0]);
        if (std::abs(det) < 1e-9f) return std::nullopt;

        const float invdet = 1.0f / det;
        std::array<std::array<float, 3>, 3> inv{};

        inv[0][0] =  (m[1][1]*m[2][2] - m[1][2]*m[2][1]) * invdet;
        inv[0][1] = -(m[0][1]*m[2][2] - m[0][2]*m[2][1]) * invdet;
        inv[0][2] =  (m[0][1]*m[1][2] - m[0][2]*m[1][1]) * invdet;
        inv[1][0] = -(m[1][0]*m[2][2] - m[1][2]*m[2][0]) * invdet;
        inv[1][1] =  (m[0][0]*m[2][2] - m[0][2]*m[2][0]) * invdet;
        inv[1][2] = -(m[0][0]*m[1][2] - m[0][2]*m[1][0]) * invdet;
        inv[2][0] =  (m[1][0]*m[2][1] - m[1][2]*m[2][0]) * invdet;
        inv[2][1] = -(m[0][0]*m[2][1] - m[0][2]*m[2][0]) * invdet;
        inv[2][2] =  (m[0][0]*m[1][1] - m[0][1]*m[1][0]) * invdet;

        return inv;
    }

    std::chrono::microseconds timeout_duration_;
    std::chrono::microseconds last_valid_time_{0};
    bool gate_passed_{false};
    bool navigation_lost_{false};
};
