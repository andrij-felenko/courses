#pragma once

#include <chrono>
#include <cstdint>
#include <expected>
#include <span>
#include <string_view>

#include "blackbox.hpp"
#include "deadman.hpp"
#include "hardware.hpp"
#include "link.hpp"
#include "slewclock.hpp"

namespace cart {

// П'ять станів автономної деградації зі статті.
enum class State : std::uint8_t { Online, HoldPhase1, AutonomousPhase2, SafeStatePhase3, Reconnecting };
std::string_view describe(State s) noexcept;

inline constexpr Millis kTick           = 20ms;
inline constexpr Millis kDeadmanTimeout = 250ms;   // дозвіл, що його поновлює лише свіжий кадр
inline constexpr Millis kHeartbeat      = 20ms;    // період імпульсів на лінію ENABLE
inline constexpr Millis kPhase1Timeout  = 5s;
inline constexpr Millis kPhase2Timeout  = 60s;
inline constexpr Millis kReconnectHold  = 1s;

inline constexpr float kMaxAccel = 0.6f;   // межа другої похідної (одиниць тяги/с)
inline constexpr float kMaxJerk  = 3.0f;   // межа третьої похідної (одиниць тяги/с²)
inline constexpr float kDecel    = 0.5f;   // безпечне сповільнення у фазі 2
inline constexpr float kSteerRate = 1.5f;
inline constexpr float kMaxSpeed  = 2.0f;

// Числення шляху у фазі 1: невизначеність росте тим швидше, чим швидше їдемо.
inline constexpr float kSigmaBase  = 0.05f;
inline constexpr float kSigmaGain  = 0.25f;
inline constexpr float kSigmaLimit = 1.0f;   // радіус безпеки, метри

inline constexpr Millis kBeaconPeriod = 3s;
inline constexpr Millis kBeaconFlash  = 100ms;

// Токен-бакет фонового зливу: ~20% смуги радіо, решта — свіжим пакетам.
inline constexpr std::size_t kDrainCreditPerTick = 12;
inline constexpr std::size_t kDrainCreditMax     = 240;

namespace event {
inline constexpr std::uint8_t kLinkLost      = 0x01;
inline constexpr std::uint8_t kPhase2        = 0x02;
inline constexpr std::uint8_t kSafeState     = 0x03;
inline constexpr std::uint8_t kDeadReckoning = 0x04;
inline constexpr std::uint8_t kReconnect     = 0xA1;
inline constexpr std::uint8_t kOnline        = 0xA2;
std::string_view describe(std::uint8_t code) noexcept;
}  // namespace event

class FallbackController {
public:
    FallbackController(Board& board, std::uint32_t key);

    // Сирий кадр з ефіру. Час беремо з плати — зайвого аргументу тут не треба.
    std::expected<void, LinkError> handleFrame(std::span<const std::byte> frame);
    void tick(float sensorValue);

    [[nodiscard]] State state() const noexcept { return state_; }
    [[nodiscard]] float throttle() const noexcept { return throttle_; }
    [[nodiscard]] Millis offlineFor() const noexcept;

    [[nodiscard]] const BlackBox& log() const noexcept { return log_; }
    [[nodiscard]] const Link& link() const noexcept { return link_; }
    [[nodiscard]] const Deadman& deadman() const noexcept { return deadman_; }
    [[nodiscard]] const SlewClock& clock() const noexcept { return clock_; }

private:
    void enter(State next, Millis now, std::uint8_t code, bool critical);
    void rampThrottle(float target, float dt);
    void rampSteering(float target, float dt);

    Board&    board_;
    SlewClock clock_;
    Deadman   deadman_;
    Link      link_;
    BlackBox  log_;

    State  state_{State::Online};
    Millis stateSince_{0};
    Millis lastFrame_{0};
    Millis offlineSince_{0};
    Millis lastRaw_{0};

    Command cached_{};   // остання довірена уставка
    float throttle_{0.0f};
    float throttleRate_{0.0f};   // темп зміни уставки — його й обмежує ривок
    float steering_{0.0f};

    float drPos_{0.0f};     // числення шляху у фазі 1
    float drSigma_{0.0f};

    Millis      beaconPhase_{0};
    std::size_t drainCredit_{0};
};

}  // namespace cart
