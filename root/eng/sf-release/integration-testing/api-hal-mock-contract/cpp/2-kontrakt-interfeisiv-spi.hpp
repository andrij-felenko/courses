#pragma once

#include <cstdint>
#include <cstddef>
#include <span>
#include <expected>
#include <functional>
#include <chrono>

namespace embedded::hal {

enum class Status : uint8_t {
    Ok = 0,
    InvalidParameter,
    Busy,
    Timeout,
    Nack,
    HardwareFault
};

enum class PinState : uint8_t {
    Reset = 0,
    Set   = 1
};

/* --- Інтерфейс драйвера GPIO --- */
class IGpioDriver {
public:
    virtual ~IGpioDriver() = default;
    virtual Status writePin(uint16_t pin, PinState state) noexcept = 0;
    virtual std::expected<PinState, Status> readPin(uint16_t pin) noexcept = 0;
    virtual Status togglePin(uint16_t pin) noexcept = 0;
};

/* --- Інтерфейс драйвера SPI --- */
using SpiTransferCallback = std::function<void(Status status)>;

class ISpiBus {
public:
    virtual ~ISpiBus() = default;
    virtual Status transferBlocking(std::span<const uint8_t> tx_buf,
                                    std::span<uint8_t> rx_buf,
                                    std::chrono::milliseconds timeout) noexcept = 0;
    virtual Status transferAsync(std::span<const uint8_t> tx_buf,
                                  std::span<uint8_t> rx_buf,
                                  SpiTransferCallback callback) noexcept = 0;
};

/* --- Інтерфейс драйвера I2C --- */
class II2cDriver {
public:
    virtual ~II2cDriver() = default;
    virtual Status memRead(uint16_t dev_addr,
                           uint16_t mem_addr,
                           size_t mem_addr_size,
                           std::span<uint8_t> data,
                           std::chrono::milliseconds timeout) noexcept = 0;
    virtual Status masterTransmit(uint16_t dev_addr,
                                  std::span<const uint8_t> data,
                                  std::chrono::milliseconds timeout) noexcept = 0;
};

} // namespace embedded::hal
