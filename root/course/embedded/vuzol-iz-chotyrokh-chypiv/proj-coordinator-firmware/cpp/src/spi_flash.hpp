#pragma once

// NOR Flash W25Q128JV на SPI1. Запуск стирання й програмування не чекає
// завершення: чи чип звільнився, питає автомат журналу.

#include <cstddef>
#include <cstdint>
#include <expected>
#include <span>

#include "mcu.hpp"

namespace node {

enum class FlashError : std::uint8_t {
    Busy,          // попередня операція ще йде
    OutOfRange,    // адреса поза 16 МБ або запис через межу сторінки
    NotAccepted,   // чип не прийняв команду (WEL не встановився)
    WrongChip,     // JEDEC ID не той
};

template <typename T>
using FlashResult = std::expected<T, FlashError>;

class SpiFlash {
public:
    void begin() noexcept;

    FlashResult<void> probe() noexcept;
    FlashResult<void> read(std::uint32_t addr, std::span<std::byte> dst) noexcept;
    FlashResult<void> startPageProgram(std::uint32_t addr, std::span<const std::byte> src) noexcept;
    FlashResult<void> startSectorErase(std::uint32_t sectorAddr) noexcept;

    [[nodiscard]] bool busy() noexcept;

    // Успішна команда сама знімає WEL. Якщо BUSY уже немає, а WEL стоїть —
    // чип команду відкинув; іншої ознаки помилки запису в нього немає.
    [[nodiscard]] bool lastOperationAccepted() noexcept;

private:
    // Вибір кристала як власник ресурсу: підняти CS не можна забути, і саме
    // це підняття запускає у чипа програмування чи стирання.
    class ChipSelect {
    public:
        explicit ChipSelect(const mcu::Pin& cs) noexcept : cs_{cs} { cs_.write(false); }
        ~ChipSelect() { cs_.write(true); }

        ChipSelect(const ChipSelect&) = delete;
        ChipSelect& operator=(const ChipSelect&) = delete;

    private:
        const mcu::Pin& cs_;
    };

    std::uint8_t transfer(std::uint8_t out) noexcept;
    void sendAddress(std::uint32_t addr) noexcept;
    std::uint8_t readStatus1() noexcept;
    void writeEnable() noexcept;

    mcu::Pin cs_{GPIOA, 4};
    mcu::Pin sck_{GPIOA, 5};
    mcu::Pin miso_{GPIOA, 6};
    mcu::Pin mosi_{GPIOA, 7};
};

}  // namespace node
