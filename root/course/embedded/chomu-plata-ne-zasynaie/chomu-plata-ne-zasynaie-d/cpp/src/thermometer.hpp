// thermometer.hpp — датчик на комутованій шині.
//
// Помилка шини тут — значення, а не -1 з errno: std::expected змушує
// викликача розібрати випадок, коли раб тримає SDA внизу й дві підтяжки
// по 10 кОм палять струм усю паузу між вимірами.
#pragma once

#include <cstdint>
#include <expected>
#include <span>

#include "soc.hpp"

namespace sensor {

enum class BusError : std::uint8_t {
    Timeout,
    Nack,
    Arbitration,
    Busy,
    Stuck // SDA не відпущена навіть після дев'яти тактів вивільнення
};

struct Celsius {
    std::int16_t halfDegrees{};

    [[nodiscard]] constexpr int whole() const noexcept { return halfDegrees / 2; }
    [[nodiscard]] constexpr bool hasHalf() const noexcept { return (halfDegrees % 2) != 0; }
};

[[nodiscard]] bool busStuck() noexcept;
[[nodiscard]] std::expected<void, BusError> recoverBus() noexcept;

// Сеанс роботи з шиною. Відкриття вмикає тактування й блок I2C,
// вихід із області видимості гасить обидва — увімкнений периферійний
// блок споживає і в сні.
class BusSession {
public:
    [[nodiscard]] static std::expected<BusSession, BusError> open() noexcept;

    ~BusSession() noexcept;

    BusSession(BusSession&& other) noexcept : live_{other.live_} { other.live_ = false; }

    BusSession(const BusSession&) = delete;
    BusSession& operator=(const BusSession&) = delete;
    BusSession& operator=(BusSession&&) = delete;

    [[nodiscard]] std::expected<void, BusError> readRegister(std::uint8_t address7,
                                                             std::uint8_t reg,
                                                             std::span<std::uint8_t> out) const noexcept;

private:
    BusSession() noexcept = default;

    bool live_{true};
};

class Thermometer {
public:
    explicit constexpr Thermometer(std::uint8_t address7) noexcept : address_{address7} {}

    // LM75-сумісний: два байти, знакове значення в старших дев'яти бітах.
    [[nodiscard]] std::expected<Celsius, BusError> read(const BusSession& bus) const noexcept;

private:
    std::uint8_t address_;
};

} // namespace sensor
