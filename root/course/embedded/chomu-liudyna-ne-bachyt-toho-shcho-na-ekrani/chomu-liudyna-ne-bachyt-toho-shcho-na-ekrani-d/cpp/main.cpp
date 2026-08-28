#include <chrono>
#include <cmath>
#include <optional>

namespace Telemetry {

enum class Severity {
    Normal = 0,
    Warning,
    Critical
};

struct Thresholds {
    float warn_limit{0.0f};
    float crit_limit{0.0f};
    float max_drift_rate{0.0f};  // Поріг швидкості дрейфу для захисту від Change Blindness
};

class MetricChannel {
public:
    explicit MetricChannel(Thresholds thresholds) : limits_(thresholds) {}

    void update(float new_val, std::chrono::milliseconds now) {
        if (last_time_) {
            const float dt = std::chrono::duration<float>(now - *last_time_).count();
            if (dt > 0.005f) {
                const float raw_rate = std::abs(new_val - value_) / dt;
                filtered_rate_ = (ema_alpha_ * raw_rate) + ((1.0f - ema_alpha_) * filtered_rate_);
            }
        }

        value_ = new_val;
        last_time_ = now;

        // Оцінка небезпеки за рівнем або швидкістю дрейфу
        if (value_ >= limits_.crit_limit) {
            severity_ = Severity::Critical;
        } else if (value_ >= limits_.warn_limit ||
                  (limits_.max_drift_rate > 0.0f && filtered_rate_ >= limits_.max_drift_rate)) {
            severity_ = Severity::Warning;
        } else {
            severity_ = Severity::Normal;
        }
    }

    [[nodiscard]] float value() const noexcept { return value_; }
    [[nodiscard]] float rate() const noexcept { return filtered_rate_; }
    [[nodiscard]] Severity severity() const noexcept { return severity_; }

private:
    Thresholds limits_;
    float value_{0.0f};
    float filtered_rate_{0.0f};
    Severity severity_{Severity::Normal};
    std::optional<std::chrono::milliseconds> last_time_{std::nullopt};
    static constexpr float ema_alpha_{0.20f};
};

} // namespace Telemetry
