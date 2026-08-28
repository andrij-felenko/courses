#include <cstdint>
#include <cmath>
#include <array>
#include <span>
#include <algorithm>

namespace edge {

/**
 * @brief Шаблонний кільцевий буфер фіксованого розміру без динамічної пам'яті.
 */
template <typename T, std::size_t Capacity>
class RingBuffer {
public:
    constexpr RingBuffer() noexcept = default;

    void push(const T& item) noexcept {
        buffer_[head_] = item;
        head_ = (head_ + 1) % Capacity;
        if (count_ < Capacity) {
            ++count_;
        }
    }

    [[nodiscard]] constexpr std::size_t size() const noexcept {
        return count_;
    }

    [[nodiscard]] constexpr std::size_t capacity() const noexcept {
        return Capacity;
    }

    void copy_linear(std::span<T> dest) const noexcept {
        const std::size_t to_copy = std::min(dest.size(), count_);
        std::size_t start = (head_ + Capacity - count_) % Capacity;
        for (std::size_t i = 0; i < to_copy; ++i) {
            dest[i] = buffer_[(start + i) % Capacity];
        }
    }

    void clear() noexcept {
        head_ = 0;
        count_ = 0;
    }

private:
    std::array<T, Capacity> buffer_{};
    std::size_t head_{0};
    std::size_t count_{0};
};

/**
 * @brief Потоковий статистичний акумулятор Велфорда.
 */
class WelfordAccumulator {
public:
    constexpr WelfordAccumulator() noexcept = default;

    void update(float x) noexcept {
        ++count_;
        const float delta = x - mean_;
        mean_ += delta / static_cast<float>(count_);
        const float delta2 = x - mean_;
        m2_ += delta * delta2;
    }

    [[nodiscard]] constexpr uint32_t count() const noexcept {
        return count_;
    }

    [[nodiscard]] constexpr float mean() const noexcept {
        return mean_;
    }

    [[nodiscard]] float variance() const noexcept {
        return (count_ > 1) ? (m2_ / static_cast<float>(count_ - 1)) : 0.0f;
    }

    [[nodiscard]] float stddev() const noexcept {
        return std::sqrt(variance());
    }

    [[nodiscard]] float z_score(float x) const noexcept {
        const float s = stddev();
        if (s < 1e-6f) return 0.0f;
        return std::abs(x - mean_) / s;
    }

    void reset() noexcept {
        count_ = 0;
        mean_ = 0.0f;
        m2_ = 0.0f;
    }

private:
    uint32_t count_{0};
    float mean_{0.0f};
    float m2_{0.0f};
};

enum class TelemetryAction : uint8_t {
    Discard,
    Heartbeat,
    AnomalyAlarm
};

struct TelemetryReport {
    TelemetryAction action{TelemetryAction::Discard};
    float value{0.0f};
    float running_mean{0.0f};
    float running_stddev{0.0f};
    float z_score{0.0f};
    uint32_t timestamp_ms{0};
};

/**
 * @brief Модуль бортового аналізу та адаптивної компресії телеметрії.
 */
template <std::size_t SnapshotSize = 32>
class AnomalyDetector {
public:
    struct Config {
        float deadband{0.5f};
        float z_threshold{3.0f};
        uint32_t heartbeat_interval_ms{60000};
        uint32_t min_training_samples{30};
    };

    explicit constexpr AnomalyDetector(const Config& cfg = {}) noexcept
        : config_(cfg) {}

    TelemetryReport process_sample(float raw_sample, uint32_t current_time_ms) noexcept {
        TelemetryReport report;
        report.value = raw_sample;
        report.timestamp_ms = current_time_ms;

        snapshot_ring_.push(raw_sample);

        bool is_anomaly = false;
        float z = 0.0f;

        if (stats_.count() >= config_.min_training_samples) {
            z = stats_.z_score(raw_sample);
            if (z > config_.z_threshold) {
                is_anomaly = true;
            }
        }

        if (!is_anomaly) {
            stats_.update(raw_sample);
        }

        report.running_mean = stats_.mean();
        report.running_stddev = stats_.stddev();
        report.z_score = z;

        if (is_anomaly) {
            report.action = TelemetryAction::AnomalyAlarm;
            last_transmitted_value_ = raw_sample;
            last_heartbeat_ms_ = current_time_ms;
            return report;
        }

        const float delta = std::abs(raw_sample - last_transmitted_value_);
        const bool heartbeat_due = (current_time_ms - last_heartbeat_ms_) >= config_.heartbeat_interval_ms;

        if (delta >= config_.deadband || heartbeat_due) {
            report.action = TelemetryAction::Heartbeat;
            last_transmitted_value_ = raw_sample;
            last_heartbeat_ms_ = current_time_ms;
        } else {
            report.action = TelemetryAction::Discard;
        }

        return report;
    }

    void extract_snapshot(std::span<float> dest) const noexcept {
        snapshot_ring_.copy_linear(dest);
    }

    [[nodiscard]] const WelfordAccumulator& statistics() const noexcept {
        return stats_;
    }

    void reset() noexcept {
        stats_.reset();
        snapshot_ring_.clear();
        last_transmitted_value_ = 0.0f;
        last_heartbeat_ms_ = 0;
    }

private:
    Config config_{};
    WelfordAccumulator stats_{};
    RingBuffer<float, SnapshotSize> snapshot_ring_{};
    float last_transmitted_value_{0.0f};
    uint32_t last_heartbeat_ms_{0};
};

} // namespace edge
