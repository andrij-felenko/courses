#include <cstdint>
#include <cmath>
#include <optional>
#include <span>
#include <algorithm>

enum class SensorHealthFlags : uint8_t {
    Ok              = 0x00,
    OutOfRangeLow   = 0x01,
    OutOfRangeHigh  = 0x02,
    SlewRate        = 0x04,
    ZeroVariance    = 0x08,
    CrossCheck      = 0x10
};

[[nodiscard]] constexpr SensorHealthFlags operator|(SensorHealthFlags a, SensorHealthFlags b) noexcept {
    return static_cast<SensorHealthFlags>(static_cast<uint8_t>(a) | static_cast<uint8_t>(b));
}

[[nodiscard]] constexpr bool has_flag(SensorHealthFlags mask, SensorHealthFlags flag) noexcept {
    return (static_cast<uint8_t>(mask) & static_cast<uint8_t>(flag)) != 0;
}

struct SensorGuardConfig {
    float min_plausible;
    float max_plausible;
    float max_slew_rate;
    float min_variance;
    uint32_t min_samples_var;
};

struct QuorumResult {
    float voted_value{0.0f};
    bool quorum_valid{false};
    uint8_t faulty_sensor_mask{0};
};

class SensorHealthGuard {
public:
    explicit constexpr SensorHealthGuard(const SensorGuardConfig& config) noexcept
        : cfg_(config) {}

    SensorHealthFlags update(float value, uint32_t timestamp_ms) noexcept;

    [[nodiscard]] float mean() const noexcept { return mean_; }
    [[nodiscard]] float variance() const noexcept;
    [[nodiscard]] SensorHealthFlags current_flags() const noexcept { return flags_; }
    [[nodiscard]] bool is_healthy() const noexcept { return flags_ == SensorHealthFlags::Ok; }

    static QuorumResult vote_2oo3(float s1, float s2, float s3, float max_allowed_spread) noexcept;

private:
    SensorGuardConfig cfg_;
    float last_value_{0.0f};
    uint32_t last_timestamp_ms_{0};
    bool has_prev_sample_{false};

    uint32_t sample_count_{0};
    float mean_{0.0f};
    float m2_{0.0f};

    SensorHealthFlags flags_{SensorHealthFlags::Ok};
};
