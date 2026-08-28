#include <cstdint>
#include <cmath>
#include <optional>
#include <span>
#include <concepts>

enum class SensorError : uint8_t {
    Ok             = 0x00,
    RangeLow       = 0x01,
    RangeHigh      = 0x02,
    SlewRate       = 0x04,
    ZeroVariance   = 0x08,
    CrossCheck     = 0x10
};

[[nodiscard]] constexpr SensorError operator|(SensorError a, SensorError b) noexcept {
    return static_cast<SensorError>(static_cast<uint8_t>(a) | static_cast<uint8_t>(b));
}

[[nodiscard]] constexpr bool has_error(SensorError mask, SensorError err) noexcept {
    return (static_cast<uint8_t>(mask) & static_cast<uint8_t>(err)) != 0;
}

struct SensorGuardConfig {
    float min_valid;
    float max_valid;
    float max_gradient_per_s;
    float min_noise_variance;
    uint32_t variance_window;
};

class SensorGuard {
public:
    explicit constexpr SensorGuard(const SensorGuardConfig& cfg) noexcept
        : cfg_(cfg) {}

    SensorError process(float sample, uint32_t now_ms) noexcept;

    [[nodiscard]] float mean() const noexcept { return mean_; }
    [[nodiscard]] float variance() const noexcept;
    [[nodiscard]] SensorError status() const noexcept { return status_; }
    [[nodiscard]] bool is_valid() const noexcept { return status_ == SensorError::Ok; }

private:
    SensorGuardConfig cfg_;
    float prev_val_{0.0f};
    uint32_t prev_ts_ms_{0};
    bool has_history_{false};

    uint32_t count_{0};
    float mean_{0.0f};
    float m2_{0.0f};

    SensorError status_{SensorError::Ok};
};
