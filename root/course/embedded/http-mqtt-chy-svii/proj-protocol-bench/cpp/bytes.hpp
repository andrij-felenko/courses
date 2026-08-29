// Побайтовий запис і читання полів + CRC-16-CCITT (C++23).
//
// Замість запакованої структури й memcpy тут явний потік байтів. Це трохи
// більше коду, зате порядок байтів кожного поля видно в самому рядку, кадр
// збирається однаково на little- і big-endian машині, а читання ніколи не
// розіменовує невирівняну адресу — тобто HardFault на Cortex-M0 неможливий
// за побудовою.
#pragma once

#include <cstddef>
#include <cstdint>
#include <span>
#include <string_view>

namespace telem {

class ByteWriter {
public:
    explicit constexpr ByteWriter(std::span<std::uint8_t> buf) noexcept : buf_{buf} {}

    constexpr ByteWriter& u8(std::uint8_t v) noexcept
    {
        put(v);
        return *this;
    }

    constexpr ByteWriter& u16le(std::uint16_t v) noexcept
    {
        put(static_cast<std::uint8_t>(v & 0xFF));
        put(static_cast<std::uint8_t>(v >> 8));
        return *this;
    }

    constexpr ByteWriter& i16le(std::int16_t v) noexcept
    {
        return u16le(static_cast<std::uint16_t>(v));
    }

    constexpr ByteWriter& u32le(std::uint32_t v) noexcept
    {
        for (int shift = 0; shift < 32; shift += 8) {
            put(static_cast<std::uint8_t>((v >> shift) & 0xFF));
        }
        return *this;
    }

    // MQTT тримає всі свої 16-бітні поля у зворотному порядку — big-endian.
    constexpr ByteWriter& u16be(std::uint16_t v) noexcept
    {
        put(static_cast<std::uint8_t>(v >> 8));
        put(static_cast<std::uint8_t>(v & 0xFF));
        return *this;
    }

    constexpr ByteWriter& raw(std::span<const std::uint8_t> src) noexcept
    {
        for (const auto b : src) {
            put(b);
        }
        return *this;
    }

    constexpr ByteWriter& raw(std::string_view src) noexcept
    {
        for (const auto c : src) {
            put(static_cast<std::uint8_t>(c));
        }
        return *this;
    }

    // Переповнення не кидає й не обриває запис на півслові: writer просто
    // перестає бути ok(), і викликач бачить це один раз наприкінці, замість
    // перевіряти кожне поле окремо.
    [[nodiscard]] constexpr bool ok() const noexcept { return ok_; }
    [[nodiscard]] constexpr std::size_t size() const noexcept { return pos_; }

    [[nodiscard]] constexpr std::span<const std::uint8_t> written() const noexcept
    {
        return buf_.first(pos_);
    }

private:
    constexpr void put(std::uint8_t b) noexcept
    {
        if (pos_ < buf_.size()) {
            buf_[pos_++] = b;
        } else {
            ok_ = false;
        }
    }

    std::span<std::uint8_t> buf_;
    std::size_t pos_{};
    bool ok_{true};
};

class ByteReader {
public:
    explicit constexpr ByteReader(std::span<const std::uint8_t> buf) noexcept : buf_{buf} {}

    constexpr std::uint8_t u8() noexcept { return get(); }

    constexpr std::uint16_t u16le() noexcept
    {
        const auto lo = get();
        const auto hi = get();
        return static_cast<std::uint16_t>(lo | (hi << 8));
    }

    constexpr std::int16_t i16le() noexcept
    {
        return static_cast<std::int16_t>(u16le());
    }

    constexpr std::uint32_t u32le() noexcept
    {
        std::uint32_t v = 0;
        for (int shift = 0; shift < 32; shift += 8) {
            v |= static_cast<std::uint32_t>(get()) << shift;
        }
        return v;
    }

    [[nodiscard]] constexpr bool ok() const noexcept { return ok_; }

private:
    constexpr std::uint8_t get() noexcept
    {
        if (pos_ < buf_.size()) {
            return buf_[pos_++];
        }
        ok_ = false;
        return 0;
    }

    std::span<const std::uint8_t> buf_;
    std::size_t pos_{};
    bool ok_{true};
};

// CRC-16-CCITT: поліном 0x1021, початкове значення 0xFFFF, без відображення.
// constexpr — тож контрольну суму сталого кадру можна порахувати ще на етапі
// компіляції й покласти в тест як очікуване число.
[[nodiscard]] constexpr std::uint16_t crc16Ccitt(std::span<const std::uint8_t> data) noexcept
{
    std::uint16_t crc = 0xFFFF;
    for (const auto byte : data) {
        crc ^= static_cast<std::uint16_t>(static_cast<std::uint16_t>(byte) << 8);
        for (int bit = 0; bit < 8; ++bit) {
            if ((crc & 0x8000) != 0) {
                crc = static_cast<std::uint16_t>((crc << 1) ^ 0x1021);
            } else {
                crc = static_cast<std::uint16_t>(crc << 1);
            }
        }
    }
    return crc;
}

}  // namespace telem
