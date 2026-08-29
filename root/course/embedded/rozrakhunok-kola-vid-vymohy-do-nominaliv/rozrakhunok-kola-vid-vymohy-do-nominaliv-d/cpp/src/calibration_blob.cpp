#include "calibration_blob.hpp"

#include <algorithm>
#include <bit>

namespace psu::nvm {
namespace {

constexpr std::array<std::byte, 4> magic{
    std::byte{'C'}, std::byte{'A'}, std::byte{'L'}, std::byte{'1'}};

constexpr std::size_t payloadSize = 12;   // усе, крім двох байтів CRC

void putU32(std::span<std::byte, 4> dst, std::uint32_t value) noexcept {
    for (std::size_t i = 0; i < 4; ++i) {
        dst[i] = static_cast<std::byte>((value >> (8 * i)) & 0xFFu);
    }
}

[[nodiscard]] std::uint32_t getU32(std::span<const std::byte, 4> src) noexcept {
    std::uint32_t value = 0;
    for (std::size_t i = 0; i < 4; ++i) {
        value |= static_cast<std::uint32_t>(std::to_integer<std::uint8_t>(src[i])) << (8 * i);
    }
    return value;
}

} // namespace

std::string_view describe(BlobError err) noexcept {
    switch (err) {
        case BlobError::shortBuffer: return "замалий буфер";
        case BlobError::badMagic:    return "запису калібрування немає";
        case BlobError::badCrc:      return "CRC не збігся";
        case BlobError::implausible: return "коефіцієнти поза смугою";
    }
    return "невідома помилка";
}

/* CRC-16/CCITT-FALSE: поліном 0x1021, початкове значення 0xFFFF,
   без відображення бітів і без фінального XOR. Табличний варіант тут зайвий —
   14 байтів раз на завантаження не варті 512 байтів Flash під таблицю. */
std::uint16_t crc16Ccitt(std::span<const std::byte> data) noexcept {
    std::uint16_t crc = 0xFFFFu;
    for (const std::byte b : data) {
        crc ^= static_cast<std::uint16_t>(std::to_integer<std::uint8_t>(b) << 8);
        for (int bit = 0; bit < 8; ++bit) {
            crc = (crc & 0x8000u) ? static_cast<std::uint16_t>((crc << 1) ^ 0x1021u)
                                  : static_cast<std::uint16_t>(crc << 1);
        }
    }
    return crc;
}

Blob pack(const Calibration& cal) noexcept {
    Blob blob{};
    std::ranges::copy(magic, blob.begin());
    /* Знакове значення кладемо його бітовим поданням: std::bit_cast не залежить
       від того, як платформа подає від'ємні числа. */
    putU32(std::span<std::byte, 4>{blob.data() + 4, 4}, std::bit_cast<std::uint32_t>(cal.offsetMv));
    putU32(std::span<std::byte, 4>{blob.data() + 8, 4}, cal.gainPpm);

    const auto crc = crc16Ccitt(std::span<const std::byte>{blob}.first(payloadSize));
    blob[12] = static_cast<std::byte>(crc & 0xFFu);
    blob[13] = static_cast<std::byte>((crc >> 8) & 0xFFu);
    return blob;
}

std::expected<Calibration, BlobError> unpack(std::span<const std::byte> raw) noexcept {
    if (raw.size() < blobSize) {
        return std::unexpected{BlobError::shortBuffer};
    }
    if (!std::ranges::equal(raw.first(magic.size()), magic)) {
        return std::unexpected{BlobError::badMagic};
    }

    const auto stored = static_cast<std::uint16_t>(
        std::to_integer<std::uint8_t>(raw[12])
        | (std::to_integer<std::uint16_t>(raw[13]) << 8));
    if (stored != crc16Ccitt(raw.first(payloadSize))) {
        return std::unexpected{BlobError::badCrc};
    }

    Calibration cal{};
    cal.offsetMv = std::bit_cast<std::int32_t>(getU32(std::span<const std::byte, 4>{raw.data() + 4, 4}));
    cal.gainPpm  = getU32(std::span<const std::byte, 4>{raw.data() + 8, 4});

    /* CRC ловить биті байти, але не ловить помилки самого калібрування:
       нахил 3.0 міг бути порахований і записаний цілком коректно. */
    if (!cal.plausible()) {
        return std::unexpected{BlobError::implausible};
    }
    return cal;
}

} // namespace psu::nvm
