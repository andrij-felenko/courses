#pragma once

#include <chrono>
#include <cstddef>
#include <cstdint>
#include <expected>
#include <optional>
#include <span>
#include <string_view>

#include "dfu_protocol.hpp"

namespace fc::flash {

// Карта Flash STM32F405: 4*16K + 1*64K + 7*128K = 1 МБ.
inline constexpr std::uint32_t kBase = 0x0800'0000;
inline constexpr std::uint32_t kTotalSize = 1024u * 1024u;
// Перші два сектори по 16 КБ займає сам завантажувач.
inline constexpr std::uint32_t kApplicationBase = 0x0800'8000;

inline constexpr std::uint8_t kRead = 0x1;
inline constexpr std::uint8_t kErase = 0x2;
inline constexpr std::uint8_t kWrite = 0x4;

struct Sector {
    std::uint32_t address;
    std::uint32_t size;
    std::uint8_t index;   // номер для поля SNB регістра FLASH_CR
    std::uint8_t access;  // комбінація kRead | kErase | kWrite

    [[nodiscard]] constexpr bool erasable() const noexcept { return (access & kErase) != 0; }
};

[[nodiscard]] std::span<const Sector> sectors() noexcept;
[[nodiscard]] std::optional<Sector> sector_at(std::uint32_t address) noexcept;
[[nodiscard]] bool in_application(std::uint32_t address, std::size_t length) noexcept;
[[nodiscard]] std::chrono::milliseconds erase_timeout(const Sector& sector) noexcept;
[[nodiscard]] std::chrono::milliseconds application_erase_timeout() noexcept;

// Рядок карти пам'яті DfuSe кладемо в чужий буфер: купи в завантажувачі немає.
[[nodiscard]] std::string_view layout_string(std::span<char> out) noexcept;
// Той самий рядок як USB String Descriptor (UTF-16LE).
[[nodiscard]] std::span<const std::byte> layout_descriptor(std::span<std::byte> out) noexcept;

// Flash відображена в адресний простір — читання віддає вигляд без копії.
[[nodiscard]] std::span<const std::byte> read(std::uint32_t address, std::size_t length) noexcept;
[[nodiscard]] bool application_image_valid() noexcept;

// RAII навколо FLASH_CR.LOCK: доки живий об'єкт — пам'ять відкрита на запис.
class Controller {
public:
    Controller() noexcept;
    ~Controller();

    Controller(const Controller&) = delete;
    Controller& operator=(const Controller&) = delete;

    [[nodiscard]] std::expected<void, dfu::Status> erase(std::uint32_t address) noexcept;
    [[nodiscard]] std::expected<void, dfu::Status> erase_application() noexcept;
    [[nodiscard]] std::expected<void, dfu::Status> program(std::uint32_t address,
                                                          std::span<const std::byte> data) noexcept;
};

}  // namespace fc::flash
