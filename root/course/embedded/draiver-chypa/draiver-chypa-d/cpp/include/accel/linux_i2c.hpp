// linux_i2c.hpp — Рівень 1 поверх драйвера /dev/i2c-N.
//
// Дескриптор належить об'єктові: закривати його вручну нікому не треба й
// нікому не можна забути. Копіювання заборонене, переміщення дозволене —
// саме так шина потрапляє всередину драйвера, не втрачаючи власника.
#pragma once

#include <chrono>
#include <cstdint>
#include <span>
#include <string>

#include "status.hpp"
#include "transport.hpp"

namespace accel {

class LinuxI2cBus {
public:
    // address — семибітна адреса з даташита (0x19), без біта напрямку:
    // зсув на один біт робить контролер шини, а не прикладний код.
    [[nodiscard]] static Result<LinuxI2cBus> open(const std::string &devicePath,
                                                  std::uint8_t address) noexcept;

    LinuxI2cBus(const LinuxI2cBus &) = delete;
    LinuxI2cBus &operator=(const LinuxI2cBus &) = delete;
    LinuxI2cBus(LinuxI2cBus &&other) noexcept;
    LinuxI2cBus &operator=(LinuxI2cBus &&other) noexcept;
    ~LinuxI2cBus();

    [[nodiscard]] Result<void> read(std::uint8_t reg, std::span<std::uint8_t> rx) noexcept;
    [[nodiscard]] Result<void> write(std::uint8_t reg, std::span<const std::uint8_t> tx) noexcept;
    void delay(std::chrono::milliseconds pause) noexcept;

    [[nodiscard]] std::uint8_t address() const noexcept { return address_; }

private:
    LinuxI2cBus(int fd, std::uint8_t address) noexcept : fd_(fd), address_(address) {}
    void closeDescriptor() noexcept;

    int          fd_{-1};
    std::uint8_t address_{0};
};

static_assert(BusTransport<LinuxI2cBus>,
              "шина мусить задовольняти контракт Рівня 1");

} // namespace accel
