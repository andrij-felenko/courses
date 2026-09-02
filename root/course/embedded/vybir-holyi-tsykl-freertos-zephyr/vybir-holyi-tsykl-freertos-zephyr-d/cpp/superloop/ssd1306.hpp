#pragma once

// SSD1306 128x64. Кадровий буфер живе в об'єкті як std::array — жодного
// malloc, розмір відомий лінкеру, а flush() сам міряє, скільки він блокував.
#include "board.hpp"

#include <algorithm>
#include <array>
#include <cstdint>
#include <expected>
#include <span>

namespace app {

class Ssd1306 {
public:
    static constexpr std::size_t kCols = 128;
    static constexpr std::size_t kPages = 8;

    std::expected<void, board::BusError> begin() noexcept
    {
        static constexpr std::array<std::uint8_t, 25> kInit{
            0xAE, 0xD5, 0x80, 0xA8, 0x3F, 0xD3, 0x00, 0x40, 0x8D, 0x14,
            0x20, 0x00, 0xA1, 0xC8, 0xDA, 0x12, 0x81, 0x7F, 0xD9, 0xF1,
            0xDB, 0x40, 0xA4, 0xA6, 0xAF};

        board::SpiBus::reset_pin(false);
        spin(20000);
        board::SpiBus::reset_pin(true);
        spin(20000);

        for (std::uint8_t c : kInit) {
            if (auto r = command(c); !r) { return r; }
        }
        clear();
        return {};
    }

    void clear() noexcept { fb_.fill(0U); }

    void bar(std::size_t page, std::int32_t value, std::int32_t lo, std::int32_t hi) noexcept
    {
        const std::int32_t span = hi - lo;
        if ((span <= 0) || (page >= kPages)) { return; }

        value = std::clamp(value, lo, hi);
        const std::int32_t width = ((value - lo) * static_cast<std::int32_t>(kCols)) / span;
        auto row = std::span{fb_}.subspan(page * kCols, kCols);
        for (std::size_t x = 0; x < kCols; ++x) {
            row[x] = (static_cast<std::int32_t>(x) < width) ? 0x3CU : 0x00U;
        }
    }

    void number(std::size_t x, std::size_t page, std::int32_t value, std::size_t decimals) noexcept
    {
        std::array<std::uint8_t, 10> digits{};
        std::size_t n = 0;
        std::uint32_t v;

        if (value < 0) {
            put(x, page, 0x04U); // мінус
            put(x + 1, page, 0x04U);
            x += 3;
            v = static_cast<std::uint32_t>(-value);
        } else {
            v = static_cast<std::uint32_t>(value);
        }

        do {
            digits[n++] = static_cast<std::uint8_t>(v % 10U);
            v /= 10U;
        } while ((v != 0U) && (n < digits.size()));

        while (n <= decimals) {
            digits[n++] = 0U; // доводимо до вигляду 0.xx
        }

        while (n > 0) {
            --n;
            x = glyph(x, page, digits[n]);
            if ((decimals != 0) && (n == decimals)) {
                put(x, page, 0x10U); // кома
                x += 2;
            }
        }
    }

    // Повертає, скільки цикл простояв на цьому кадрі.
    std::expected<board::ms, board::BusError> flush() noexcept
    {
        static constexpr std::array<std::uint8_t, 6> kWindow{0x21, 0x00, 0x7F, 0x22, 0x00, 0x07};

        const board::ms started = board::now();
        for (std::uint8_t c : kWindow) {
            if (auto r = command(c); !r) { return std::unexpected{r.error()}; }
        }
        board::SpiBus::data_mode(true);
        board::SpiBus::select(true);
        auto written = board::SpiBus::write(fb_);
        board::SpiBus::select(false);

        if (!written) { return std::unexpected{written.error()}; }
        return board::now() - started;
    }

private:
    // Цифри 3x5: байт — стовпчик, біт 0 угорі.
    static constexpr std::array<std::array<std::uint8_t, 3>, 10> kFont{{
        {0x1F, 0x11, 0x1F}, {0x02, 0x1F, 0x00}, {0x19, 0x15, 0x17}, {0x11, 0x15, 0x1F},
        {0x07, 0x04, 0x1F}, {0x17, 0x15, 0x1D}, {0x1F, 0x15, 0x1C}, {0x01, 0x01, 0x1F},
        {0x1F, 0x15, 0x1F}, {0x07, 0x15, 0x1F}}};

    static void spin(int cycles) noexcept
    {
        for (volatile int i = 0; i < cycles; ++i) { }
    }

    static std::expected<void, board::BusError> command(std::uint8_t c) noexcept
    {
        board::SpiBus::data_mode(false);
        board::SpiBus::select(true);
        auto r = board::SpiBus::write(std::span{&c, 1});
        board::SpiBus::select(false);
        return r;
    }

    void put(std::size_t x, std::size_t page, std::uint8_t bits) noexcept
    {
        if ((x < kCols) && (page < kPages)) {
            fb_[page * kCols + x] |= bits;
        }
    }

    std::size_t glyph(std::size_t x, std::size_t page, std::uint8_t digit) noexcept
    {
        for (std::size_t c = 0; c < 3; ++c) {
            put(x + c, page, kFont[digit][c]);
        }
        return x + 4;
    }

    std::array<std::uint8_t, kCols * kPages> fb_{};
};

} // namespace app
