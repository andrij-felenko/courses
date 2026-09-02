// address.hpp — 7-бітна адреса I2C як тип, який неможливо зсунути двічі.
// Зсув живе рівно в одному місці, а число з даташита проходить перевірку
// на вході, а не після третьої години з логічним аналізатором.
#pragma once

#include <cstdint>
#include <expected>

namespace i2c {

inline constexpr std::uint8_t kFirstAddr = 0x08;
inline constexpr std::uint8_t kLastAddr = 0x77;

enum class AddrError : std::uint8_t {
    reserved, // 0x00..0x07 і 0x78..0x7F — службові діапазони стандарту
    shifted,  // > 0x7F: у даташиті надрукований вже зсунутий байт кадру
};

struct AddrProblem {
    AddrError kind;
    std::uint8_t suggested; // що, найімовірніше, мали на увазі
};

class Address {
  public:
    [[nodiscard]] static constexpr std::expected<Address, AddrProblem>
    from_7bit(std::uint8_t value) noexcept
    {
        if (value < kFirstAddr || value > kLastAddr) {
            return std::unexpected(AddrProblem{AddrError::reserved, value});
        }
        return Address{value};
    }

    // Число «як надруковано в даташиті»: одні виробники дають 7 біт (0x68),
    // інші — готові байти кадру (0xD0/0xD1). Розрізняємо тут, один раз.
    [[nodiscard]] static constexpr std::expected<Address, AddrProblem>
    from_datasheet(std::uint8_t printed) noexcept
    {
        if (printed > 0x7F) {
            return std::unexpected(AddrProblem{
                AddrError::shifted, static_cast<std::uint8_t>(printed >> 1)});
        }
        return from_7bit(printed);
    }

    [[nodiscard]] constexpr std::uint8_t value() const noexcept { return v_; }

    [[nodiscard]] constexpr std::uint8_t write_byte() const noexcept
    {
        return static_cast<std::uint8_t>(v_ << 1);
    }

    [[nodiscard]] constexpr std::uint8_t read_byte() const noexcept
    {
        return static_cast<std::uint8_t>((v_ << 1) | 1u);
    }

    friend constexpr bool operator==(Address, Address) noexcept = default;

  private:
    explicit constexpr Address(std::uint8_t value) noexcept : v_{value} {}

    std::uint8_t v_;
};

// Арифметику кадру перевіряє компілятор, а не плата: 0x68 → 0xD0 і 0xD1.
static_assert(Address::from_datasheet(0x68)->write_byte() == 0xD0);
static_assert(Address::from_datasheet(0x68)->read_byte() == 0xD1);
// А 0xD0, поданий як адреса, — це не пристрій 0xD0, а той самий 0x68.
static_assert(Address::from_datasheet(0xD0).error().suggested == 0x68);

} // namespace i2c
