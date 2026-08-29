#pragma once

#include <expected>

#include "link.hpp"

// Два перетворення, без яких кадр не існує: контрольна сума й байт-стафінг.
namespace link::codec {

// CRC-16-CCITT: G(x) = x^16 + x^12 + x^5 + 1 (0x1021), початкове значення 0xFFFF,
// без відображення бітів і без фінального XOR.
//
// Властивість, задля якої обрано саме цей варіант: CRC над блоком РАЗОМ із дописаною
// до нього сумою дорівнює нулю. Приймач перевіряє кадр однією дією.
[[nodiscard]] constexpr std::uint16_t crc16_ccitt(Bytes data) noexcept {
    std::uint16_t crc = 0xFFFF;
    for (const std::uint8_t byte : data) {
        crc ^= static_cast<std::uint16_t>(static_cast<std::uint16_t>(byte) << 8);
        for (int bit = 0; bit < 8; ++bit) {
            crc = (crc & 0x8000) ? static_cast<std::uint16_t>((crc << 1) ^ 0x1021)
                                 : static_cast<std::uint16_t>(crc << 1);
        }
    }
    return crc;
}

[[nodiscard]] constexpr std::size_t cobs_max_encoded(std::size_t len) noexcept {
    return len + len / 254 + 1;
}

// Межі буфера тримає std::span: код зміщення прийшов із лінії, де його міг
// перевернути шум, тож довіряти йому не можна ні на байт.
[[nodiscard]] std::expected<std::size_t, Error> cobs_encode(
    Bytes src, std::span<std::uint8_t> dst) noexcept;

[[nodiscard]] std::expected<std::size_t, Error> cobs_decode(
    Bytes src, std::span<std::uint8_t> dst) noexcept;

}  // namespace link::codec
