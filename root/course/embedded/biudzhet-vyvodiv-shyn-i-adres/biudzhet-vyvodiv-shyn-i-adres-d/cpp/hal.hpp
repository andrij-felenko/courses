#pragma once

#include <cstdint>
#include <expected>
#include <span>

namespace board {

/* Помилка обміну. Аргумент відділено від шинних збоїв навмисно: на
   IO-помилку драйвер лікує залізо, на Argument — програміст лікує виклик. */
enum class BusError { Argument, Nack, Bus, Timeout };

template <class T>
using Result = std::expected<T, BusError>;

inline constexpr std::uint8_t kNoPin = 0xFFu;

/* Контракт драйвера I2C конкретного мікроконтролера. */
class I2cBus {
public:
    virtual ~I2cBus() = default;

    virtual Result<void> write(std::uint8_t addr,
                               std::span<const std::uint8_t> data) = 0;
    virtual Result<void> read(std::uint8_t addr,
                              std::span<std::uint8_t> buffer) = 0;
    /* Запис, повторний старт, читання — однією неподільною транзакцією. */
    virtual Result<void> writeRead(std::uint8_t addr,
                                   std::span<const std::uint8_t> out,
                                   std::span<std::uint8_t> in) = 0;

    Result<void> writeRegister(std::uint8_t addr, std::uint8_t reg,
                               std::uint8_t value) {
        const std::uint8_t frame[]{reg, value};
        return write(addr, frame);
    }

    Result<std::uint8_t> readRegister(std::uint8_t addr, std::uint8_t reg) {
        const std::uint8_t out[]{reg};
        std::uint8_t value{};
        if (auto r = writeRead(addr, out, std::span{&value, 1}); !r) {
            return std::unexpected(r.error());
        }
        return value;
    }
};

/* Контракт SPI. Порожній rx — прийняте відкидається; порожній tx — на MOSI
   подаються одиниці (типове читання з Flash чи картки). */
class SpiBus {
public:
    virtual ~SpiBus() = default;
    virtual Result<void> transfer(std::span<const std::uint8_t> tx,
                                  std::span<std::uint8_t> rx) = 0;
};

/* Дискретні виводи мікроконтролера. */
class GpioPort {
public:
    virtual ~GpioPort() = default;
    virtual void write(std::uint8_t pin, bool high) = 0;
    virtual bool read(std::uint8_t pin) = 0;
    virtual void delayUs(std::uint32_t us) = 0;
};

}  // namespace board
