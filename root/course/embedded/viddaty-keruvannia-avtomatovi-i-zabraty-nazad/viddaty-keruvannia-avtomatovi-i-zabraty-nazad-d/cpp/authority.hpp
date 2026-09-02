#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <optional>
#include <span>
#include <string_view>

#include "rc_link.hpp"
#include "types.hpp"

namespace fc {

enum class Phase : std::uint8_t {
    AutoNav = 0,
    OverrideIn,
    ManualHold,
    HandbackWait,
    BlendingOut
};

enum class Event : std::uint8_t {
    OverrideBegin,
    ManualFull,
    HandbackArmed,
    AutoResumed,
    ThrottleEngaged,
    RcLost,
    FenceReclaim
};

[[nodiscard]] constexpr std::string_view to_string(Phase p) noexcept {
    switch (p) {
        case Phase::AutoNav:      return "AUTO_NAV";
        case Phase::OverrideIn:   return "OVERRIDE_IN";
        case Phase::ManualHold:   return "MANUAL_HOLD";
        case Phase::HandbackWait: return "HANDBACK_WAIT";
        case Phase::BlendingOut:  return "BLENDING_OUT";
    }
    return "?";
}

// Ваги пілота окремо для орієнтації й окремо для газу.
struct Authority {
    float attitude{};
    float throttle{};
};

struct Status {
    Phase phase{Phase::AutoNav};
    Authority alpha{};
    bool freeze_nav{false};  // заморозити інтегратори й підтягувати уставку
    bool request_rtl{false}; // зв'язку немає — переходимо на аварійний план
};

[[nodiscard]] ControlCommand blend(const Authority& a,
                                   const ControlCommand& autopilot,
                                   const ControlCommand& pilot) noexcept;

class AuthorityManager {
public:
    struct Config {
        float deadband{0.12f};          // 12% ходу ручки
        Seconds blend_in{0.20f};        // наростання авторитету пілота
        Seconds blend_out{0.40f};       // повернення авторитету автоматові
        Seconds handback_hold{1.50f};   // утримання нейтралі перед поверненням
        float throttle_move_rate{0.20f}; // 1/с — рух важеля, а не його положення
        Seconds throttle_rate_tau{0.10f};
    };

    explicit AuthorityManager(Config cfg = {}) noexcept : cfg_(cfg) {}

    // Порожній optional означає втрату радіозв'язку.
    Status update(const std::optional<RcCommand>& rc, bool fence_breach, Seconds dt) noexcept;

    // Події поточного кроку; живуть до наступного виклику update().
    [[nodiscard]] std::span<const Event> events() const noexcept {
        return {events_.data(), event_count_};
    }

private:
    void emit(Event e) noexcept;
    [[nodiscard]] bool attitude_deflected(const RcCommand& rc) const noexcept;
    [[nodiscard]] Status status(bool request_rtl) const noexcept;

    static constexpr float kActiveEps = 0.02f;
    static constexpr std::size_t kMaxEvents = 4;

    Config cfg_;
    Phase phase_{Phase::AutoNav};
    Authority alpha_{};
    Seconds hold_timer_{0.0f};
    float throttle_prev_{0.0f};
    float throttle_rate_{0.0f};
    bool throttle_engaged_{false};
    bool prev_switch_manual_{false};
    bool fence_latched_{false};
    bool rc_lost_{false};
    bool primed_{false};

    std::array<Event, kMaxEvents> events_{};
    std::size_t event_count_{0};
};

} // namespace fc
