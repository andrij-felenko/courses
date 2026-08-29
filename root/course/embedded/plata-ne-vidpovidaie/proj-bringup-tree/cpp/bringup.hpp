// Публічний інтерфейс діагностичної прошивки. Помилка тут — значення, а не
// код повернення: std::expected не дає мовчки пройти повз провал фази.
#pragma once

#include "mmio.hpp"

#include <array>
#include <cstdint>
#include <expected>
#include <optional>
#include <span>

namespace bringup {

enum class Error : std::uint8_t {
    hse_timeout,     // кварц не збудився
    pll_timeout,     // петля не захопила частоту
    i2c_timeout,     // модуль не дійшов до наступного стану
    i2c_nack,        // адресу ніхто не підтвердив
    i2c_bus_stuck,   // SDA лишилася притиснутою після дев'яти тактів
    adc_timeout      // перетворення не завершилося
};

template <class T>
using Result = std::expected<T, Error>;

// ---- фаза 1 ----
struct ClockStatus {
    bool hsi_ready{};
    bool hse_ready{};
    bool pll_ready{};
};

[[nodiscard]] Result<ClockStatus> verify_clocks() noexcept;

// ---- фаза 2 ----
[[nodiscard]] std::span<const mmio::Pin> default_testpoints() noexcept;
void exercise_testpoints(std::span<const mmio::Pin> pins, std::uint32_t cycles) noexcept;

// ---- фаза 3 ----
// Володіння модулем I2C: доки об'єкт живий, периферія ввімкнена й тримає
// виводи. Деструктор знімає PE — це той самий `goto out`, тільки такий,
// про який не можна забути на новій гілці помилки.
class I2cBus {
public:
    static constexpr std::uint8_t first_address = 0x08;
    static constexpr std::uint8_t last_address = 0x77;

    [[nodiscard]] static Result<I2cBus> open(std::uint32_t pclk_hz = mmio::pclk1_hz) noexcept;

    I2cBus(const I2cBus&) = delete;
    I2cBus& operator=(const I2cBus&) = delete;
    I2cBus(I2cBus&& other) noexcept;
    I2cBus& operator=(I2cBus&& other) noexcept;
    ~I2cBus() noexcept;

    // Чи довелося розблоковувати шину перед стартом модуля.
    [[nodiscard]] bool bus_was_stuck() const noexcept { return bus_was_stuck_; }

    [[nodiscard]] Result<void> probe(std::uint8_t address_7bit) noexcept;
    [[nodiscard]] Result<std::size_t> scan(std::span<std::uint8_t> found) noexcept;

private:
    explicit I2cBus(bool bus_was_stuck) noexcept : bus_was_stuck_{bus_was_stuck} {}
    void release() noexcept;

    bool bus_was_stuck_{};
    bool owns_peripheral_{true};
};

// ---- фаза 4 ----
struct SupplyMeasurement {
    std::uint16_t vrefint_raw{};
    std::uint16_t factory_cal{};   // 0 — комірку не запрограмовано
    std::uint32_t vdda_mv{};
    bool nominal_fallback{};       // рахували за типовим 1.21 В, не за калібруванням
};

[[nodiscard]] Result<SupplyMeasurement> measure_vdda() noexcept;

// ---- звіт, який читає відлагоджувач ----
struct Report {
    std::optional<ClockStatus> clocks;
    std::optional<Error> clock_error;

    bool i2c_bus_was_stuck{};
    std::size_t i2c_found{};
    std::array<std::uint8_t, 8> i2c_addresses{};
    std::optional<Error> i2c_error;

    std::optional<SupplyMeasurement> supply;
    std::optional<Error> supply_error;
};

}  // namespace bringup
