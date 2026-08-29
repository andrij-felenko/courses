#pragma once

#include <chrono>
#include <cstdint>
#include <mutex>
#include <span>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

#include "posix_fd.hpp"

namespace gw {

enum class ModbusErrc {
    Io,         // збій вводу-виводу або порт зник із системи
    Timeout,    // підлеглий мовчить
    Crc,        // кадр побився в дорозі
    Frame,      // чужий адресат або не та функція
    Exception,  // підлеглий відповів кодом винятку Modbus
};

class ModbusError : public std::runtime_error {
public:
    ModbusError(ModbusErrc code, std::string_view what, std::uint8_t exceptionCode = 0)
        : std::runtime_error{std::string{what}}, code_{code}, exceptionCode_{exceptionCode} {}

    [[nodiscard]] ModbusErrc code() const noexcept { return code_; }
    [[nodiscard]] std::uint8_t exceptionCode() const noexcept { return exceptionCode_; }

private:
    ModbusErrc code_;
    std::uint8_t exceptionCode_;
};

// Майстер Modbus RTU поверх RS-485. Порт один на весь польовий сегмент, а
// звертаються до нього дві задачі — опитувач і правило автономії, — тому
// обмін серіалізовано м'ютексом усередині класу.
class ModbusMaster {
public:
    ModbusMaster(const std::string& device, int baud, std::chrono::milliseconds timeout);

    std::vector<std::uint16_t> readHolding(std::uint8_t slave, std::uint16_t start,
                                           std::uint16_t count);
    void writeCoil(std::uint8_t slave, std::uint16_t address, bool on);

    // Пара регістрів → float32 IEEE 754, старше слово першим.
    [[nodiscard]] static float regsToFloat(std::span<const std::uint16_t, 2> regs) noexcept;

private:
    std::vector<std::uint8_t> transact(std::span<const std::uint8_t> request);

    Fd fd_;
    std::chrono::milliseconds timeout_;
    std::mutex mutex_;
};

}  // namespace gw
