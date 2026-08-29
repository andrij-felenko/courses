// SpiEmergencyDump.hpp — автономне вивантаження тому в SPI FRAM або NOR Flash.
// Жодного DMA, жодних переривань, жодної RTOS: усе опитуванням регістрів.
// Помилку віддаємо через std::expected — у панічному контексті виняток
// розкручувати нічим, а мовчазний -1 у такому місці нікому не потрібен.
#pragma once

#include <cstddef>
#include <cstdint>
#include <expected>
#include <span>

namespace embedded::drivers {

enum class FlushError : std::uint8_t {
    Timeout,    // SPI не відповів у відведену кількість обертів
    NoDevice,   // мікросхема не підняла біт дозволу запису
    NotErased   // сектор NOR Flash не стерли заздалегідь
};

using FlushResult = std::expected<void, FlushError>;

class EmergencySpiMemory {
public:
    constexpr EmergencySpiMemory(std::uintptr_t spi_base, std::uintptr_t cs_bsrr,
                                 std::uint32_t cs_pin) noexcept
        : spi_base_{spi_base}, cs_bsrr_{cs_bsrr}, cs_pin_{cs_pin} {}

    // FRAM пише на швидкості шини й не потребує стирання: увесь том іде
    // однією транзакцією, від виклику до останнього байта — мілісекунди.
    [[nodiscard]] FlushResult write_fram(std::uint32_t dst_addr,
                                         std::span<const std::byte> image) const noexcept;

    // NOR Flash програмує сторінками по 256 байтів і лише в стерті комірки,
    // тож сектор під дамп стирають заздалегідь, на справному запуску.
    [[nodiscard]] FlushResult erase_flash_slot(std::uint32_t dst_addr,
                                               std::size_t size) const noexcept;
    [[nodiscard]] FlushResult write_flash(std::uint32_t dst_addr,
                                          std::span<const std::byte> image) const noexcept;

private:
    // Chip Select як об'єкт: лінія піднімається на будь-якому виході з
    // транзакції, зокрема на ранньому return по помилці.
    class ChipSelect {
    public:
        explicit ChipSelect(const EmergencySpiMemory& bus) noexcept;
        ~ChipSelect();
        ChipSelect(const ChipSelect&) = delete;
        ChipSelect& operator=(const ChipSelect&) = delete;

    private:
        const EmergencySpiMemory& bus_;
    };

    [[nodiscard]] FlushResult takeover() const noexcept;
    [[nodiscard]] std::expected<std::uint8_t, FlushError> xfer(std::uint8_t out) const noexcept;
    [[nodiscard]] FlushResult send(std::uint8_t byte) const noexcept;
    [[nodiscard]] FlushResult send_command(std::uint8_t opcode, std::uint32_t addr) const noexcept;
    [[nodiscard]] std::expected<std::uint8_t, FlushError> read_status() const noexcept;
    [[nodiscard]] FlushResult write_enable() const noexcept;
    [[nodiscard]] FlushResult wait_write_done() const noexcept;
    [[nodiscard]] FlushResult verify_head(std::uint32_t dst_addr,
                                          std::span<const std::byte> image) const noexcept;

    std::uintptr_t spi_base_;
    std::uintptr_t cs_bsrr_;
    std::uint32_t  cs_pin_;
};

// SPI1 на STM32F4, Chip Select — PA4.
inline constexpr EmergencySpiMemory kNvBus{0x40013000U, 0x40020000U + 0x18U, 4U};

// Почистити кеш даних і віддати том носієві. Це те, що викликає обробник збою.
[[nodiscard]] FlushResult dump_recorder_to_fram(std::uint32_t dst_addr) noexcept;
[[nodiscard]] FlushResult prepare_flash_slot(std::uint32_t dst_addr) noexcept;

} // namespace embedded::drivers
