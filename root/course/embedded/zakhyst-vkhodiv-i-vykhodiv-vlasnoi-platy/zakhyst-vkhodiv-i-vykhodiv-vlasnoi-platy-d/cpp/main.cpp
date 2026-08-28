// Ідіоматичний C++20 модуль моніторингу захисту портів
#include <cstdint>
#include <expected>
#include <array>
#include <span>

enum class GuardFault : std::uint8_t {
    None = 0,
    OvercurrentTrip,
    ThermalShutdown,
    PermanentLockout
};

class InputDebounceFilter {
public:
    static constexpr std::uint32_t DebounceTimeMs = 20;

    constexpr InputDebounceFilter() = default;

    constexpr bool update(bool rawState, std::uint32_t currentTimeMs) noexcept {
        history_ = static_cast<std::uint8_t>((history_ << 1) | (rawState ? 1U : 0U));

        if (history_ == 0xFFU) {
            if (!stableState_ && (currentTimeMs - lastTransitionMs_ >= DebounceTimeMs)) {
                stableState_ = true;
                lastTransitionMs_ = currentTimeMs;
            }
        } else if (history_ == 0x00U) {
            if (stableState_ && (currentTimeMs - lastTransitionMs_ >= DebounceTimeMs)) {
                stableState_ = false;
                lastTransitionMs_ = currentTimeMs;
            }
        }
        return stableState_;
    }

    [[nodiscard]] constexpr bool state() const noexcept { return stableState_; }

private:
    std::uint8_t history_{0};
    bool stableState_{false};
    std::uint32_t lastTransitionMs_{0};
};

template <std::size_t MaxRetries = 3>
class SmartOutputGuard {
public:
    static constexpr std::uint32_t CoolDownPeriodMs = 5000;

    constexpr SmartOutputGuard() = default;

    constexpr void triggerEnable() noexcept {
        if (fault_ != GuardFault::PermanentLockout) {
            enabled_ = true;
            fault_ = GuardFault::None;
        }
    }

    [[nodiscard]] constexpr bool isEnabled() const noexcept { return enabled_; }
    [[nodiscard]] constexpr GuardFault currentFault() const noexcept { return fault_; }

    constexpr std::expected<void, GuardFault> processFaultPin(bool faultPinActive, std::uint32_t currentTimeMs) noexcept {
        if (faultPinActive && enabled_) {
            enabled_ = false;
            lastFaultTimeMs_ = currentTimeMs;
            ++retryCount_;

            if (retryCount_ >= MaxRetries) {
                fault_ = GuardFault::PermanentLockout;
                return std::unexpected(GuardFault::PermanentLockout);
            }
            fault_ = GuardFault::OvercurrentTrip;
            return std::unexpected(GuardFault::OvercurrentTrip);
        }

        // Автоматичне відновлення після охолодження
        if (!enabled_ && fault_ == GuardFault::OvercurrentTrip) {
            if (currentTimeMs - lastFaultTimeMs_ >= CoolDownPeriodMs) {
                enabled_ = true;
                fault_ = GuardFault::None;
            }
        }

        return {};
    }

private:
    bool enabled_{false};
    GuardFault fault_{GuardFault::None};
    std::uint8_t retryCount_{0};
    std::uint32_t lastFaultTimeMs_{0};
};
