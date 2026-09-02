#pragma once

#include <chrono>
#include <cstdint>
#include <string_view>

namespace manual_control {

using Millis  = std::chrono::milliseconds;
using Seconds = std::chrono::duration<float>;

/* Пороги зі статті. Час — у типах <chrono>, тож переплутати мілісекунди
 * з секундами компілятор не дасть. */
inline constexpr std::int16_t kRcDeadband         = 50;   // 5% від [-1000..1000]
inline constexpr std::int16_t kRcThrottleDeadband = 100;
inline constexpr Millis       kRcLinkTimeout{100};
inline constexpr Millis       kGcsDegrade{250};
inline constexpr Millis       kGcsFailsafe{1000};
inline constexpr std::int16_t kHoverThrottle      = 500;
inline constexpr float        kAxisSlewPerSec     = 4000.0F;

struct Axes {
    std::int16_t  roll{};      // [-1000..1000], позитивний — вправо
    std::int16_t  pitch{};     // [-1000..1000], позитивний — вперед
    std::int16_t  throttle{};  // [0..1000]
    std::int16_t  yaw{};       // [-1000..1000], позитивний — за годинниковою
    std::uint16_t buttons{};

    [[nodiscard]] bool deflected() const noexcept;
};

enum class State : std::uint8_t { Disarmed, RcActive, GcsActive, GcsDegraded, Failsafe };
enum class FailsafeAction : std::uint8_t { None, ReturnToLaunch, Land };
enum class ArmVerdict : std::uint8_t {
    Accepted,
    NeedsConfirmation,  // перший запит на арм відхиляємо завжди
    NoLink,
    StickNotNeutral,
    InFailsafe,
    Disarmed
};

/* Лімітер швидкості наростання однієї осі. Стан у float: при dt = 2.5 мс крок
 * дорівнює 10 одиницям, і цілочисельне округлення вниз просто спинило б вісь. */
class SlewLimiter {
public:
    void reset(std::int16_t value) noexcept { value_ = static_cast<float>(value); }
    [[nodiscard]] std::int16_t step(std::int16_t target, Seconds dt) noexcept;

private:
    float value_{0.0F};
};

class Arbiter {
public:
    struct Counters {
        std::uint32_t preemptions{};
        std::uint32_t degradations{};
        std::uint32_t failsafes{};
    };

    Arbiter() noexcept = default;

    void setHomeAvailable(bool ok) noexcept { homeValid_ = ok; }

    // Кадр фізичного пульта (CRSF/ExpressLRS/S.BUS уже розібрано).
    void feedRc(const Axes& rc, Millis now) noexcept;

    // Осі MANUAL_CONTROL #69: x — тангаж, y — крен, z — тяга, r — рискання.
    void feedManualControl(std::int16_t x, std::int16_t y, std::int16_t z,
                           std::int16_t r, std::uint16_t buttons, Millis now) noexcept;

    // Арм/дизарм лише окремою командою, ніяких комбінацій стіків.
    [[nodiscard]] ArmVerdict requestArm(bool arm, bool confirmed, Millis now) noexcept;

    // Викликається з такту контуру стабілізації (400 Гц), не з приходу пакета.
    void update(Millis now, Seconds dt) noexcept;

    [[nodiscard]] State state() const noexcept { return state_; }
    [[nodiscard]] FailsafeAction failsafe() const noexcept { return failsafe_; }
    [[nodiscard]] bool armed() const noexcept { return armed_; }
    [[nodiscard]] const Axes& output() const noexcept { return out_; }
    [[nodiscard]] const Axes& gcsRaw() const noexcept { return gcs_; }
    [[nodiscard]] const Counters& counters() const noexcept { return counters_; }

private:
    void latchOutput(const Axes& axes) noexcept;
    void driveTo(const Axes& target, Seconds dt) noexcept;

    State          state_{State::Disarmed};
    FailsafeAction failsafe_{FailsafeAction::None};
    bool           armed_{false};
    bool           homeValid_{false};
    bool           rcLinkLost_{true};

    Axes out_{};
    Axes rc_{};
    Axes gcs_{};

    SlewLimiter slewRoll_, slewPitch_, slewYaw_, slewThrottle_;

    Millis lastRc_{0};
    Millis lastGcs_{0};
    bool   rcSeen_{false};
    bool   gcsSeen_{false};

    Counters counters_{};
};

[[nodiscard]] std::string_view toString(State s) noexcept;
[[nodiscard]] std::string_view toString(FailsafeAction f) noexcept;
[[nodiscard]] std::string_view toString(ArmVerdict v) noexcept;

}  // namespace manual_control
