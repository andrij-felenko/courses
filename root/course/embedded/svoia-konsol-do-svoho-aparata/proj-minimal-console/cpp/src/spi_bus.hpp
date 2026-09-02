#pragma once

#include <chrono>
#include <cstddef>
#include <span>

#include "hal.hpp"

namespace console {

// Притискає NSS рівно на час транзакції. Вихід із будь-якої гілки — зокрема
// ранній return посеред перевірок — підіймає лінію назад.
class ChipSelect {
public:
    explicit ChipSelect(hal::Pin pin) noexcept : pin_{pin} { hal::write(pin_, false); }
    ~ChipSelect() { hal::write(pin_, true); }

    ChipSelect(const ChipSelect&) = delete;
    ChipSelect& operator=(const ChipSelect&) = delete;

private:
    hal::Pin pin_;
};

class SpiBus {
public:
    // Обмін через DMA. Кеш чіпаємо тут і тільки тут: далі по коду про нього
    // ніхто не пам'ятає, і саме так і треба.
    void transfer(std::span<const std::byte> tx, std::span<std::byte> rx) const noexcept
    {
        hal::writeback(tx);
        hal::hal_spi_xfer(reinterpret_cast<const std::uint8_t*>(tx.data()),
                          reinterpret_cast<std::uint8_t*>(rx.data()), tx.size());
        hal::invalidate(std::span<const std::byte>{rx.data(), tx.size()});
    }

    void write(std::span<const std::byte> tx) const noexcept
    {
        hal::writeback(tx);
        hal::hal_spi_xfer(reinterpret_cast<const std::uint8_t*>(tx.data()), nullptr, tx.size());
    }

    // Поки BUSY високий, чип нову команду проковтне мовчки.
    [[nodiscard]] static bool waitIdle(hal::Pin busy, std::chrono::microseconds limit) noexcept
    {
        const auto start = hal::now();
        while (hal::read(busy)) {
            if (hal::now() - start > limit) {
                return false;
            }
        }
        return true;
    }
};

}   // namespace console
