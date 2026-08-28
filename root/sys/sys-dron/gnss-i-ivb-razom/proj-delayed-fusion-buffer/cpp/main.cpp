#include <array>
#include <cstdint>
#include <cmath>
#include <optional>
#include <span>

struct Vector3 {
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};

    [[nodiscard]] constexpr Vector3 operator+(const Vector3& o) const noexcept {
        return {x + o.x, y + o.y, z + o.z};
    }
    [[nodiscard]] constexpr Vector3 operator-(const Vector3& o) const noexcept {
        return {x - o.x, y - o.y, z - o.z};
    }
    [[nodiscard]] constexpr Vector3 operator*(float s) const noexcept {
        return {x * s, y * s, z * s};
    }
    [[nodiscard]] constexpr float squared_norm() const noexcept {
        return x * x + y * y + z * z;
    }
};

struct Quaternion {
    float w{1.0f};
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};
};

struct NavState {
    uint32_t timestamp_ms{0};
    Vector3 pos{};
    Vector3 vel{};
    Quaternion q{};
    Vector3 gyro_bias{};
    Vector3 accel_bias{};
};

template <size_t Capacity = 256>
class StateHistoryBuffer {
    static_assert((Capacity & (Capacity - 1)) == 0, "Capacity must be a power of two");
public:
    constexpr StateHistoryBuffer() noexcept = default;

    void push(const NavState& state) noexcept {
        buffer_[head_ & (Capacity - 1)] = state;
        ++head_;
        if (count_ < Capacity) {
            ++count_;
        }
    }

    [[nodiscard]] std::optional<NavState> find_at(uint32_t target_time_ms) const noexcept {
        if (count_ == 0) return std::nullopt;

        const uint32_t oldest_idx = (head_ >= count_) ? (head_ - count_) : 0;
        const uint32_t oldest_time = buffer_[oldest_idx & (Capacity - 1)].timestamp_ms;
        const uint32_t newest_time = buffer_[(head_ - 1) & (Capacity - 1)].timestamp_ms;

        if (target_time_ms < oldest_time || target_time_ms > newest_time) {
            return std::nullopt;
        }

        for (size_t i = 1; i <= count_; ++i) {
            const size_t idx = (head_ - i) & (Capacity - 1);
            if (buffer_[idx].timestamp_ms <= target_time_ms) {
                return buffer_[idx];
            }
        }
        return std::nullopt;
    }

    [[nodiscard]] constexpr size_t size() const noexcept { return count_; }
    void clear() noexcept { head_ = 0; count_ = 0; }

private:
    std::array<NavState, Capacity> buffer_{};
    size_t head_{0};
    size_t count_{0};
};

class DelayedMeasurementFusion {
public:
    struct FusionResult {
        Vector3 innovation;
        float kalman_gain;
    };

    static constexpr float GateThresholdChi2_3DOF = 11.34f; /* 99% довірчий інтервал */

    [[nodiscard]] static std::optional<FusionResult> evaluate_gnss(
        const NavState& historical_state,
        const Vector3& gnss_pos,
        float pos_noise_var,
        float state_var
    ) noexcept {
        const Vector3 innovation = gnss_pos - historical_state.pos;
        const float S = state_var + pos_noise_var;

        if (S <= 1e-6f) return std::nullopt;

        const float mahalanobis_d2 = innovation.squared_norm() / S;
        if (mahalanobis_d2 > GateThresholdChi2_3DOF) {
            return std::nullopt; /* Відкидаємо аномальне вимірювання */
        }

        const float kalman_gain = state_var / S;
        return FusionResult{innovation, kalman_gain};
    }

    static void apply_feedback(NavState& current_state, const FusionResult& res) noexcept {
        current_state.pos = current_state.pos + res.innovation * res.kalman_gain;
        current_state.vel = current_state.vel + res.innovation * (res.kalman_gain * 0.45f);
    }
};
