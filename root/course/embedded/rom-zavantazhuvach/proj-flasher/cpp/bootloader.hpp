#pragma once

#include <chrono>
#include <cstdint>
#include <expected>
#include <span>
#include <string_view>
#include <vector>

#include "serial_port.hpp"

inline constexpr std::uint32_t kFlashBase = 0x08000000u;
inline constexpr std::size_t kMaxBlock = 256; // N кодується одним байтом як len-1

enum class BootError {
    Io,       // порт не прийняв або не віддав байти
    Timeout,  // завантажувач промовчав
    Nack,     // чип відмовив: немає команди або стоїть захист
    Protocol, // прийшов третій байт — розсинхронізація
    Argument
};

std::string_view describe(BootError error);

template <class T>
using Result = std::expected<T, BootError>;

struct Version {
    std::uint8_t protocol{};
    std::uint8_t option1{};
    std::uint8_t option2{};
};

// Клієнт протоколу AN3155 поверх уже налаштованого порту.
class Bootloader {
public:
    explicit Bootloader(const SerialPort& port) noexcept : port_{port} {}

    Result<void> sync();                       // 0x7F — вимірювання бітрейту
    Result<Version> version();                 // 0x01
    Result<std::uint16_t> chipId();            // 0x02
    Result<void> readoutUnprotect();           // 0x92: знімає RDP, стирає й перезавантажує чип
    Result<void> massErase();                  // 0x44 з кодом 0xFFFF
    Result<void> writeBlock(std::uint32_t address, std::span<const std::uint8_t> data); // 0x31
    Result<std::vector<std::uint8_t>> readBlock(std::uint32_t address, std::size_t length); // 0x11
    Result<void> go(std::uint32_t address);    // 0x21

private:
    Result<void> waitAck(std::chrono::milliseconds timeout);
    Result<void> command(std::uint8_t code, std::chrono::milliseconds ackTimeout);
    Result<void> address(std::uint32_t value);

    const SerialPort& port_;
};
