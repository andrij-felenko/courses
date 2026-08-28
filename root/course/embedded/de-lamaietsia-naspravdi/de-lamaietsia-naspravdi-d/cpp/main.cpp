#include <cstdint>
#include <cmath>
#include <array>
#include <span>
#include <expected>

namespace HardwareDiagnostics {

enum class HealthStatus : uint8_t {
    Ok = 0,
    Warning,
    Alarm,
    ImpactOrLooseMount
};

struct Vector3f {
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};

    [[nodiscard]] constexpr float magnitude_squared() const noexcept {
        return x * x + y * y + z * z;
    }

    [[nodiscard]] float magnitude() const noexcept {
        return std::sqrt(magnitude_squared());
    }
};

struct VibrationMetrics {
    float rms_g{0.0f};
    float crest_factor{1.0f};
    float peak_g{0.0f};
    HealthStatus status{HealthStatus::Ok};
};

template <std::size_t WindowSize = 128>
class VibrationHealthMonitor {
public:
    static_assert(WindowSize >= 16, "WindowSize must be at least 16 samples for valid statistics.");

    constexpr explicit VibrationHealthMonitor(float rms_warn = 2.5f, 
                                             float rms_alarm = 5.0f, 
                                             float crest_impact = 4.5f) noexcept
        : rms_warn_threshold_(rms_warn),
          rms_alarm_threshold_(rms_alarm),
          crest_impact_threshold_(crest_impact) {}

    // Додавання зрізу відліків (span) та обчислення метрик
    [[nodiscard]] std::expected<VibrationMetrics, bool> process_batch(std::span<const Vector3f> samples) noexcept {
        for (const auto& s : samples) {
            const float mag = s.magnitude();
            const float dynamic_accel = std::abs(mag - 1.0f); // усунення постійної 1g

            sum_sq_mag_ += dynamic_accel * dynamic_accel;
            if (dynamic_accel > peak_mag_) {
                peak_mag_ = dynamic_accel;
            }

            if (++sample_count_ >= WindowSize) {
                return finalize_window();
            }
        }
        return std::unexpected(false); // Вікно ще накопичується
    }

    void reset() noexcept {
        sum_sq_mag_ = 0.0f;
        peak_mag_ = 0.0f;
        sample_count_ = 0;
    }

private:
    float sum_sq_mag_{0.0f};
    float peak_mag_{0.0f};
    std::size_t sample_count_{0};

    const float rms_warn_threshold_;
    const float rms_alarm_threshold_;
    const float crest_impact_threshold_;

    [[nodiscard]] VibrationMetrics finalize_window() noexcept {
        const float rms = std::sqrt(sum_sq_mag_ / static_cast<float>(WindowSize));
        const float crest = (rms > 0.05f) ? (peak_mag_ / rms) : 1.0f;

        HealthStatus status = HealthStatus::Ok;
        if (crest > crest_impact_threshold_ && peak_mag_ > 2.0f) {
            status = HealthStatus::ImpactOrLooseMount;
        } else if (rms >= rms_alarm_threshold_) {
            status = HealthStatus::Alarm;
        } else if (rms >= rms_warn_threshold_) {
            status = HealthStatus::Warning;
        }

        VibrationMetrics result{
            .rms_g = rms,
            .crest_factor = crest,
            .peak_g = peak_mag_,
            .status = status
        };

        reset();
        return result;
    }
};

} // namespace HardwareDiagnostics
