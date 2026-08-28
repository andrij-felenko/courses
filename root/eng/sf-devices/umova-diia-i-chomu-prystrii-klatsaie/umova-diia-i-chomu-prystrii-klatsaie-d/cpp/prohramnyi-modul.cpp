#include <concepts>

namespace embedded::control {

template <typename T>
requires std::floating_point<T> || std::integral<T>
class HysteresisPredicate {
public:
    constexpr HysteresisPredicate(T low_threshold, T high_threshold) noexcept
        : low_(low_threshold), high_(high_threshold) {}

    [[nodiscard]] constexpr bool Update(T input_value) noexcept {
        if (!initialized_) {
            state_ = (input_value >= high_);
            initialized_ = true;
            return state_;
        }

        if (state_) {
            if (input_value <= low_) {
                state_ = false;
            }
        } else {
            if (input_value >= high_) {
                state_ = true;
            }
        }

        return state_;
    }

    [[nodiscard]] constexpr bool GetState() const noexcept { return state_; }
    constexpr void Reset() noexcept { state_ = false; initialized_ = false; }

private:
    T low_{};
    T high_{};
    bool state_{false};
    bool initialized_{false};
};

} // namespace embedded::control
