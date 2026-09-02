#pragma once

#include <array>
#include <chrono>
#include <cstdint>
#include <optional>
#include <span>

#include "types.hpp"

namespace fc {

// Позиції триточкового тумблера режимів (канал 5).
enum class FlightMode : std::uint8_t {
    Auto,    // ~1100 мкс — автономна місія
    PosHold, // ~1500 мкс — напівавтомат
    Manual   // ~1900 мкс — ручний стабілізований
};

struct RcCommand {
    float roll{};     // -1.0 ... +1.0
    float pitch{};
    float yaw{};
    float throttle{}; // 0.0 ... 1.0, важіль без повернення в нейтраль
    FlightMode mode{FlightMode::Auto};
};

// Декодер радіоканалу. Втрата зв'язку виражена порожнім optional, а не
// прапорцем усередині структури: користувач не має шансу забути перевірку.
class RcLink {
public:
    static constexpr std::size_t kChannels = 8;
    static constexpr Seconds kTimeout{0.300f}; // ~45 пропущених кадрів CRSF
    static constexpr int kDebounceFrames = 3;

    // CRSF передає 11-бітні відліки 172…1811 ↔ 988…2012 мкс.
    [[nodiscard]] static std::uint16_t crsf_ticks_to_us(std::uint16_t ticks) noexcept;

    // false — кадр побитий і стану не змінює.
    bool push(std::span<const std::uint16_t> pwm_us, Seconds now) noexcept;

    [[nodiscard]] std::optional<RcCommand> poll(Seconds now) const noexcept;

    [[nodiscard]] FlightMode mode() const noexcept { return mode_; }

private:
    static constexpr std::uint16_t kMinUs = 800;
    static constexpr std::uint16_t kMaxUs = 2200;

    std::array<std::uint16_t, kChannels> last_{};
    Seconds last_frame_{0.0f};
    bool have_frame_{false};

    FlightMode mode_{FlightMode::Auto};
    FlightMode candidate_{FlightMode::Auto};
    int candidate_count_{0};
};

} // namespace fc
