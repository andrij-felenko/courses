#include <algorithm>
#include <chrono>
#include <concepts>
#include <cstdint>
#include <functional>
#include <optional>

namespace actuators {

using namespace std::chrono_literals;

/**
 * @brief Сильний тип для представлення кутових величин у градусах
 */
struct Degrees {
    float value{0.0f};

    constexpr explicit Degrees(float v) : value(v) {}
    constexpr auto operator<=>(const Degrees&) const = default;
};

/**
 * @brief Конфігурація діапазону та калібрування сервоприводу
 */
struct ServoConfig {
    std::chrono::microseconds min_pulse{1000us};
    std::chrono::microseconds max_pulse{2000us};
    Degrees min_angle{0.0f};
    Degrees max_angle{180.0f};
    std::chrono::microseconds trim{0us};
    bool inverted{false};

    [[nodiscard]] constexpr bool is_valid() const noexcept {
        return (min_pulse < max_pulse) && (min_angle.value < max_angle.value);
    }
};

/**
 * @brief Сучасний C++ контролер сервоприводу
 */
class ServoController {
public:
    using PwmWriteCallback = std::function<void(std::chrono::microseconds)>;

    ServoController(ServoConfig config, PwmWriteCallback write_cb)
        : config_(config), write_cb_(std::move(write_cb)) {
        if (!config_.is_valid()) {
            config_ = ServoConfig{}; // Відкат до безпечних значень за замовчуванням
        }
        current_pulse_ = (config_.min_pulse + config_.max_pulse) / 2;
        current_angle_ = Degrees{(config_.min_angle.value + config_.max_angle.value) / 2.0f};
    }

    /**
     * @brief Встановлення позиції в мікросекундах із захисним обмеженням
     */
    void write_pulse(std::chrono::microseconds pulse) {
        if (!write_cb_) {
            return;
        }

        const auto target_with_trim = pulse + config_.trim;
        const auto clamped = std::clamp(target_with_trim, config_.min_pulse, config_.max_pulse);

        write_cb_(clamped);
        current_pulse_ = clamped;

        // Зворотне обчислення встановленого кута
        const float span_us = static_cast<float>((config_.max_pulse - config_.min_pulse).count());
        const float span_deg = config_.max_angle.value - config_.min_angle.value;
        float norm = static_cast<float>((clamped - config_.min_pulse).count()) / span_us;

        if (config_.inverted) {
            norm = 1.0f - norm;
        }

        current_angle_ = Degrees{config_.min_angle.value + norm * span_deg};
    }

    /**
     * @brief Встановлення цільового кута в градусах
     */
    void write_angle(Degrees angle) {
        const float clamped_deg = std::clamp(angle.value, config_.min_angle.value, config_.max_angle.value);
        const float span_deg = config_.max_angle.value - config_.min_angle.value;
        float norm = (clamped_deg - config_.min_angle.value) / span_deg;

        if (config_.inverted) {
            norm = 1.0f - norm;
        }

        const float span_us = static_cast<float>((config_.max_pulse - config_.min_pulse).count());
        const auto target_us = std::chrono::microseconds(
            static_cast<int64_t>(config_.min_pulse.count() + norm * span_us + 0.5f)
        );

        write_pulse(target_us);
    }

    [[nodiscard]] Degrees current_angle() const noexcept { return current_angle_; }
    [[nodiscard]] std::chrono::microseconds current_pulse() const noexcept { return current_pulse_; }

private:
    ServoConfig config_;
    PwmWriteCallback write_cb_;
    std::chrono::microseconds current_pulse_{1500us};
    Degrees current_angle_{90.0f};
};

} // namespace actuators
