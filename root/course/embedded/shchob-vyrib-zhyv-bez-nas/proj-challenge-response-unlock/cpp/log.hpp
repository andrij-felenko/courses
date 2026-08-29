#pragma once

#include <array>
#include <cstdint>
#include <span>
#include <string_view>

#include "hal.hpp"

namespace eolboot {

/*
 * Діагностичний журнал завантажувача. Форматуємо руками: printf і потоки
 * коштують кілька кілобайт Flash, яких у завантажувачі немає.
 */
class Log {
public:
    explicit Log(Hal& hal) noexcept : hal_(hal) {}

    void line(std::string_view text) const
    {
        prefix();
        put(text);
        put("\r\n");
    }

    void hex(std::string_view label, std::span<const std::uint8_t> data) const
    {
        prefix();
        put(label);
        for (std::size_t i = 0; i < data.size(); ++i) {
            const char pair[2] = { digit(data[i] >> 4), digit(data[i] & 0x0F) };
            put(std::string_view{ pair, sizeof pair });
            if (i + 1 < data.size()) {
                put(" ");
            }
        }
        put("\r\n");
    }

    void dec(std::string_view label, std::uint32_t value, std::string_view suffix) const
    {
        std::array<char, 10> digits{};
        std::size_t pos = digits.size();

        if (value == 0) {
            digits[--pos] = '0';
        }
        while (value != 0) {
            digits[--pos] = static_cast<char>('0' + value % 10);
            value /= 10;
        }

        prefix();
        put(label);
        put(std::string_view{ digits.data() + pos, digits.size() - pos });
        put(suffix);
        put("\r\n");
    }

    void addr(std::string_view label, std::uint32_t value, std::string_view suffix) const
    {
        std::array<char, 8> out{};
        for (std::size_t i = out.size(); i-- > 0;) {
            out[i] = digit(value & 0x0F);
            value >>= 4;
        }

        prefix();
        put(label);
        put(std::string_view{ out.data(), out.size() });
        put(suffix);
        put("\r\n");
    }

private:
    static constexpr char digit(std::uint32_t nibble) noexcept
    {
        return "0123456789ABCDEF"[nibble & 0x0F];
    }

    void prefix() const { put("[BOOT] "); }

    void put(std::string_view text) const
    {
        hal_.write({ reinterpret_cast<const std::uint8_t*>(text.data()), text.size() });
    }

    Hal& hal_;
};

} // namespace eolboot
