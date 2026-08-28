#include <iostream>
#include <cstdint>
#include <optional>

enum class TriState : uint8_t {
    False = 0,
    Unknown = 1,
    True = 2
};

class TriBool {
public:
    constexpr TriBool() noexcept : state_(TriState::Unknown) {}
    constexpr explicit TriBool(bool val) noexcept : state_(val ? TriState::True : TriState::False) {}
    constexpr explicit TriBool(TriState st) noexcept : state_(st) {}

    [[nodiscard]] constexpr TriState state() const noexcept { return state_; }
    [[nodiscard]] constexpr bool is_true() const noexcept { return state_ == TriState::True; }
    [[nodiscard]] constexpr bool is_false() const noexcept { return state_ == TriState::False; }
    [[nodiscard]] constexpr bool is_unknown() const noexcept { return state_ == TriState::Unknown; }

    /* A AND B = min(state(A), state(B)) за порядком False (0) < Unknown (1) < True (2) */
    [[nodiscard]] constexpr TriBool operator&&(TriBool rhs) const noexcept {
        const auto s1 = static_cast<uint8_t>(state_);
        const auto s2 = static_cast<uint8_t>(rhs.state_);
        return TriBool(static_cast<TriState>(s1 < s2 ? s1 : s2));
    }

    /* A OR B = max(state(A), state(B)) */
    [[nodiscard]] constexpr TriBool operator||(TriBool rhs) const noexcept {
        const auto s1 = static_cast<uint8_t>(state_);
        const auto s2 = static_cast<uint8_t>(rhs.state_);
        return TriBool(static_cast<TriState>(s1 > s2 ? s1 : s2));
    }

    /* NOT A: False <-> True, Unknown <-> Unknown */
    [[nodiscard]] constexpr TriBool operator!() const noexcept {
        if (state_ == TriState::True) return TriBool(TriState::False);
        if (state_ == TriState::False) return TriBool(TriState::True);
        return TriBool(TriState::Unknown);
    }

private:
    TriState state_;
};
