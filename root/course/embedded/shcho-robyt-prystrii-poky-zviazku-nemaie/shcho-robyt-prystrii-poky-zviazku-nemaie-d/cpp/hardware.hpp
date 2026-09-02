#pragma once

#include <array>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <expected>
#include <span>
#include <string_view>

namespace cart {

using namespace std::chrono_literals;
using Millis = std::chrono::milliseconds;

// Плата візка: Flash, силовий каскад із зовнішнім супервізором на лінії
// ENABLE і радіомодем. Помилки пам'яті повертаємо як std::expected —
// мовчазних -1 у цьому коді немає ніде.
enum class FlashError { OutOfRange, NotErased };
std::string_view describe(FlashError e) noexcept;

inline constexpr std::size_t kSectorSize  = 256;
inline constexpr std::size_t kSectorCount = 12;
inline constexpr Millis      kInterlockHold = 60ms;
inline constexpr std::size_t kRadioMtu    = 64;

class Board {
public:
    Board() noexcept { reset(); }

    Board(const Board&) = delete;
    Board& operator=(const Board&) = delete;

    [[nodiscard]] Millis now() const noexcept { return now_; }
    void advance(Millis dt) noexcept;   // рухає модельний час і обслуговує супервізор

    // Flash
    std::expected<void, FlashError> erase(std::size_t sector) noexcept;
    std::expected<void, FlashError> write(std::size_t sector, std::size_t offset,
                                          std::span<const std::byte> src) noexcept;
    std::expected<void, FlashError> read(std::size_t sector, std::size_t offset,
                                         std::span<std::byte> dst) const noexcept;
    [[nodiscard]] std::uint32_t eraseCount(std::size_t sector) const noexcept;

    // Силовий каскад
    void setSoftwareEnable(bool on) noexcept { softwareEnable_ = on; }
    [[nodiscard]] bool powered() const noexcept { return softwareEnable_ && interlockEnable_; }
    void setActuators(float throttle, float steering) noexcept;
    [[nodiscard]] float throttleOut() const noexcept { return powered() ? throttle_ : 0.0f; }
    [[nodiscard]] float steeringOut() const noexcept { return powered() ? steering_ : 0.0f; }
    void setBrake(bool on) noexcept { brake_ = on; }
    [[nodiscard]] bool brake() const noexcept { return brake_; }

    // Лінія heartbeat і сам супервізор
    void pulseInterlock() noexcept;
    [[nodiscard]] bool interlock() const noexcept { return interlockEnable_; }

    // Периферія безпечного стану
    void setBeacon(bool on) noexcept { beacon_ = on; }
    [[nodiscard]] bool beacon() const noexcept { return beacon_; }
    void setLowPower(bool on) noexcept { lowPower_ = on; }
    [[nodiscard]] bool lowPower() const noexcept { return lowPower_; }

    // Радіо
    void setRadioUp(bool up) noexcept { radioUp_ = up; }
    std::size_t send(std::span<const std::byte> data) noexcept;
    [[nodiscard]] std::uint32_t bytesSent() const noexcept { return radioBytes_; }

private:
    void reset() noexcept;
    void serviceInterlock() noexcept;

    Millis now_{0};
    std::array<std::array<std::byte, kSectorSize>, kSectorCount> flash_{};
    std::array<std::uint32_t, kSectorCount> erases_{};

    bool   softwareEnable_{false};
    bool   interlockEnable_{false};
    Millis lastPulse_{0};

    float throttle_{0.0f};
    float steering_{0.0f};
    bool  brake_{true};
    bool  beacon_{false};
    bool  lowPower_{false};

    bool          radioUp_{false};
    std::uint32_t radioBytes_{0};
};

}  // namespace cart
