#pragma once

// Ведучий I2C1 із жорсткими тайм-аутами: жодного очікування «поки не буде».
// Кожна невдача повертається як помилка, а не як тиха нуль-відповідь.

#include <cstddef>
#include <cstdint>
#include <expected>
#include <span>

#include "mcu.hpp"

namespace node {

enum class I2cError : std::uint8_t {
    Timeout,    // прапорець не з'явився за відведений час
    Nack,       // ведений не підтвердив адресу чи байт
    BusStuck,   // SDA притиснута до нуля, розблокування не помогло
};

template <typename T>
using I2cResult = std::expected<T, I2cError>;

class I2cMaster {
public:
    void begin() noexcept;

    I2cResult<void> write(std::uint8_t addr7, std::span<const std::byte> data) noexcept;
    I2cResult<void> writeRegister(std::uint8_t addr7, std::uint8_t reg, std::uint8_t value) noexcept;
    I2cResult<void> readRegisters(std::uint8_t addr7, std::uint8_t reg,
                                  std::span<std::byte> dst) noexcept;

    // Дев'ять тактів на SCL плюс коректний STOP. true — шина відпущена.
    bool recoverBus() noexcept;

    [[nodiscard]] std::uint32_t recoveries() const noexcept { return recoveries_; }

private:
    I2cResult<void> waitFor(std::uint32_t isrMask) noexcept;
    I2cResult<void> waitIdle() noexcept;
    std::unexpected<I2cError> abort(I2cError why) noexcept;

    void pinsToPeripheral() noexcept;
    void pinsToManual() noexcept;
    void peripheralSetup() noexcept;

    static constexpr std::uint32_t kTimeoutMs = 5;   // найдовша транзакція вузла

    mcu::Pin scl_{GPIOB, 6};
    mcu::Pin sda_{GPIOB, 7};
    std::uint32_t recoveries_{0};
};

}  // namespace node
