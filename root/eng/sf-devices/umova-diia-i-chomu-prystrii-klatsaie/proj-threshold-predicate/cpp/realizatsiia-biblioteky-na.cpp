#include <concepts>
#include <cstdint>
#include <type_traits>

namespace embedded::control {

/**
 * @brief Політика визначення стану при холодному старті всередині мертвої зони
 */
enum class StartupPolicy {
    ActiveOnlyAboveHigh,    // 1 лише при значенні >= high_threshold (безпечний дефолт)
    PassiveBelowLow,        // 0 лише при значенні <= low_threshold (агресивний старт)
    StrictlyInactive        // Завжди 0 на старті, доки не відбудеться перше перетинання
};

/**
 * @brief Узагальнений шаблонний клас порогового компаратора з гістерезисом
 */
template <typename T>
requires std::is_arithmetic_v<T>
class HysteresisComparator {
public:
    constexpr HysteresisComparator(T low_threshold, T high_threshold, 
                                   StartupPolicy policy = StartupPolicy::ActiveOnlyAboveHigh) noexcept
        : low_(low_threshold), high_(high_threshold), policy_(policy) {}

    /**
     * @brief Фабричний метод побудови симетричного компаратора: уставка ± (зона / 2)
     */
    static constexpr HysteresisComparator FromSetpoint(T setpoint, T deadband,
                                                       StartupPolicy policy = StartupPolicy::ActiveOnlyAboveHigh) noexcept {
        T half = deadband / static_cast<T>(2);
        return HysteresisComparator(setpoint - half, setpoint + (deadband - half), policy);
    }

    /**
     * @brief Обчислення нового стану за черговим відліком сигналу
     */
    [[nodiscard]] constexpr bool Update(T sample) noexcept {
        if (!initialized_) {
            switch (policy_) {
                case StartupPolicy::ActiveOnlyAboveHigh:
                    state_ = (sample >= high_);
                    break;
                case StartupPolicy::PassiveBelowLow:
                    state_ = (sample > low_);
                    break;
                case StartupPolicy::StrictlyInactive:
                    state_ = false;
                    break;
            }
            initialized_ = true;
            return state_;
        }

        if (state_) {
            if (sample <= low_) {
                state_ = false;
            }
        } else {
            if (sample >= high_) {
                state_ = true;
            }
        }

        return state_;
    }

    [[nodiscard]] constexpr bool State() const noexcept { return state_; }
    [[nodiscard]] constexpr bool IsInitialized() const noexcept { return initialized_; }
    
    constexpr void Reset() noexcept {
        state_ = false;
        initialized_ = false;
    }

    /**
     * @brief Безпечна зміна порогів на льоту без скидання поточного стану
     */
    constexpr void Reconfigure(T low_threshold, T high_threshold) noexcept {
        low_ = low_threshold;
        high_ = high_threshold;
    }

private:
    T low_{};
    T high_{};
    StartupPolicy policy_{StartupPolicy::ActiveOnlyAboveHigh};
    bool state_{false};
    bool initialized_{false};
};

} // namespace embedded::control
