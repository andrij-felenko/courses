#pragma once

/*
 * Контракт до заліза. Реалізацію дає BSP конкретної плати: логіка
 * розблокування знає про залізо рівно стільки, скільки тут описано.
 */

#include <cstdint>
#include <expected>
#include <optional>
#include <span>

namespace eolboot {

inline constexpr std::size_t ChipUuidLen = 16;

/* Сховище користувацьких параметрів: Wi-Fi паролі, токени, сертифікати */
inline constexpr std::uint32_t NvsBaseAddr = 0x0804'0000;
inline constexpr std::uint32_t NvsSectorSize = 4096;
inline constexpr std::uint32_t NvsSectorsCount = 8;

enum class HalError : std::uint8_t {
    EraseFailed,
    WriteFailed,
    ReadFailed,
    EfuseBurnFailed,
};

class Hal {
public:
    virtual ~Hal() = default;

    /* Апаратний генератор справжніх випадкових чисел */
    virtual void fill_random(std::span<std::uint8_t> dest) = 0;

    /* Фабричний номер кристала, зашитий заводом-виробником чіпа */
    virtual void read_chip_uuid(std::span<std::uint8_t, ChipUuidLen> dest) const = 0;

    [[nodiscard]] virtual std::uint32_t tick_ms() const noexcept = 0;

    /* Flash: стирання переводить біти в 0xFF, запис уміє лише 1 -> 0 */
    [[nodiscard]] virtual std::expected<void, HalError> erase_sector(std::uint32_t addr) = 0;
    [[nodiscard]] virtual std::expected<void, HalError> write_flash(
        std::uint32_t addr, std::span<const std::uint8_t> src) = 0;
    [[nodiscard]] virtual std::expected<void, HalError> read_flash(
        std::uint32_t addr, std::span<std::uint8_t> dest) const = 0;

    /* Комірка eFuse статусу: перепалюється один раз і незворотно */
    [[nodiscard]] virtual bool efuse_unlocked() const = 0;
    [[nodiscard]] virtual std::expected<void, HalError> burn_unlocked_efuse() = 0;

    /* Діагностичний порт (UART або USB CDC); читання неблокуюче */
    [[nodiscard]] virtual std::optional<std::uint8_t> read_byte() = 0;
    virtual void write(std::span<const std::uint8_t> data) = 0;

    [[noreturn]] virtual void reboot() = 0;
};

/* Єдиний екземпляр, який віддає BSP плати */
Hal& board_hal();

} // namespace eolboot
