// rc_safety_module.hpp - Ідіоматичний модуль безпеки польотних каналів
#pragma once

#include <cstdint>
#include <optional>
#include <expected>

namespace drone::safety {

inline constexpr uint16_t kDeadbandUs         = 25U;
inline constexpr uint16_t kThrottleArmMaxUs   = 1050U;
inline constexpr uint16_t kSwitchLowUs        = 1300U;
inline constexpr uint16_t kSwitchHighUs       = 1700U;
inline constexpr uint16_t kMinValidPulseUs    = 800U;
inline constexpr uint16_t kMaxValidPulseUs    = 2200U;

enum class ArmingError : uint16_t {
    None                = 0x0000,
    ThrottleNotZero     = 0x0001,
    PreArmMissing       = 0x0002,
    FailsafeEngaged     = 0x0004,
    SwitchNotResetBoot  = 0x0008,
    SensorNotReady      = 0x0010
};

[[nodiscard]] constexpr ArmingError operator|(ArmingError a, ArmingError b) noexcept {
    return static_cast<ArmingError>(static_cast<uint16_t>(a) | static_cast<uint16_t>(b));
}

enum class SwitchPosition : uint8_t {
    Low,
    Mid,
    High
};

struct RcInputFrame {
    uint16_t throttle_us{1000U};
    uint16_t arm_switch_us{1000U};
    uint16_t prearm_btn_us{1000U};
    uint16_t mode_switch_us{1500U};
    bool     failsafe_active{false};
    bool     sensors_healthy{true};
};

class RcSafetyManager {
public:
    constexpr RcSafetyManager() noexcept = default;

    [[nodiscard]] static std::optional<SwitchPosition> decode3Pos(uint16_t pulse_us) noexcept {
        if (pulse_us < kMinValidPulseUs || pulse_us > kMaxValidPulseUs) {
            return std::nullopt;
        }
        if (pulse_us < (kSwitchLowUs - kDeadbandUs)) {
            return SwitchPosition::Low;
        }
        if (pulse_us > (kSwitchHighUs + kDeadbandUs)) {
            return SwitchPosition::High;
        }
        return SwitchPosition::Mid;
    }

    [[nodiscard]] std::expected<bool, ArmingError> processFrame(const RcInputFrame& frame) noexcept {
        const bool arm_requested = (frame.arm_switch_us > kSwitchHighUs);
        const bool prearm_active = (frame.prearm_btn_us > kSwitchHighUs);

        // Захист від старту з увімкненим тумблером після подачі живлення
        if (switch_high_on_boot_) {
            if (!arm_requested) {
                switch_high_on_boot_ = false;
            } else {
                is_armed_ = false;
                return std::unexpected(ArmingError::SwitchNotResetBoot);
            }
        }

        // Негайне зняття з охорони
        if (!arm_requested) {
            is_armed_ = false;
            return false;
        }

        // Підтримка зведеного стану під час польоту
        if (is_armed_) {
            return true;
        }

        // Валідація інтерлоків запуску
        ArmingError errors = ArmingError::None;

        if (frame.throttle_us > kThrottleArmMaxUs) {
            errors = errors | ArmingError::ThrottleNotZero;
        }
        if (!prearm_active) {
            errors = errors | ArmingError::PreArmMissing;
        }
        if (frame.failsafe_active) {
            errors = errors | ArmingError::FailsafeEngaged;
        }
        if (!frame.sensors_healthy) {
            errors = errors | ArmingError::SensorNotReady;
        }

        if (errors != ArmingError::None) {
            is_armed_ = false;
            return std::unexpected(errors);
        }

        is_armed_ = true;
        return true;
    }

    [[nodiscard]] bool isArmed() const noexcept { return is_armed_; }

private:
    bool is_armed_{false};
    bool switch_high_on_boot_{true};
};

} // namespace drone::safety
