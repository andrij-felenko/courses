#include "sf/frame.hpp"

#include <algorithm>

namespace sf {
namespace {

constexpr std::byte kErased{0xFF};

void put_le(std::span<std::byte> dst, std::uint64_t value, std::size_t width) noexcept
{
    for (std::size_t i = 0; i < width; ++i) {
        dst[i] = static_cast<std::byte>((value >> (8 * i)) & 0xFFu);
    }
}

[[nodiscard]] std::uint64_t get_le(std::span<const std::byte> src, std::size_t width) noexcept
{
    std::uint64_t value = 0;
    for (std::size_t i = width; i-- > 0;) {
        value = (value << 8) | std::to_integer<std::uint64_t>(src[i]);
    }
    return value;
}

} // namespace

std::string_view describe(FrameError error) noexcept
{
    switch (error) {
    case FrameError::Erased:    return "стерта область";
    case FrameError::BadMagic:  return "немає преамбули";
    case FrameError::BadLength: return "неможлива довжина";
    case FrameError::Truncated: return "кадр обірвано";
    case FrameError::BadCrc:    return "контрольна сума не зійшлася";
    }
    return "невідомо";
}

// CRC-32 IEEE 802.3, віддзеркалений поліном 0xEDB88320. Побітово:
// таблиця на 256 входів з'їла б кілобайт флеші, а сканер відновлення
// працює лічені десятки мілісекунд один раз за старт.
std::uint32_t crc32(std::span<const std::byte> data) noexcept
{
    std::uint32_t crc = 0xFFFFFFFFu;

    for (std::byte b : data) {
        crc ^= std::to_integer<std::uint32_t>(b);
        for (int bit = 0; bit < 8; ++bit) {
            const std::uint32_t mask = ~(crc & 1u) + 1u; // 0xFFFFFFFF або 0
            crc = (crc >> 1) ^ (0xEDB88320u & mask);
        }
    }

    return ~crc;
}

std::expected<std::size_t, FrameError>
encode(std::span<std::byte> dst, const Header& header,
       std::span<const std::byte> payload) noexcept
{
    if (payload.size() > kMaxPayload || payload.size() != header.len) {
        return std::unexpected(FrameError::BadLength);
    }

    const std::size_t total = frame_size(header.len);
    if (dst.size() < total) {
        return std::unexpected(FrameError::Truncated);
    }

    put_le(dst.subspan(0, 2), kMagic, 2);
    put_le(dst.subspan(2, 4), header.seq, 4);
    put_le(dst.subspan(6, 8), header.ts_ms, 8);
    put_le(dst.subspan(14, 2), header.len, 2);
    dst[16] = static_cast<std::byte>(header.kind);

    std::ranges::copy(payload, dst.begin() + kHeaderSize);

    // CRC накриває заголовок разом із навантаженням: інакше збита
    // довжина пройшла б перевірку й повела сканер у нікуди.
    const auto covered = dst.first(kHeaderSize + payload.size());
    put_le(dst.subspan(kHeaderSize + payload.size(), kCrcSize), crc32(covered), 4);

    return total;
}

std::expected<Frame, FrameError> parse(std::span<const std::byte> raw) noexcept
{
    if (raw.size() < 2) {
        return std::unexpected(FrameError::Truncated);
    }

    // Стерта комірка NOR читається як 0xFF. Дві такі поспіль на місці
    // преамбули означають кінець записаного, а не пошкодження.
    if (raw[0] == kErased && raw[1] == kErased) {
        return std::unexpected(FrameError::Erased);
    }
    if (get_le(raw.first(2), 2) != kMagic) {
        return std::unexpected(FrameError::BadMagic);
    }
    if (raw.size() < kHeaderSize) {
        return std::unexpected(FrameError::Truncated);
    }

    const auto len = static_cast<std::uint16_t>(get_le(raw.subspan(14, 2), 2));
    if (len > kMaxPayload) {
        return std::unexpected(FrameError::BadLength);
    }

    const std::size_t total = frame_size(len);
    if (raw.size() < total) {
        // Заголовок обіцяє більше байтів, ніж лишилось у секторі:
        // живлення зникло між записом заголовка й навантаження.
        return std::unexpected(FrameError::Truncated);
    }

    const auto covered = raw.first(kHeaderSize + len);
    const auto stored  = static_cast<std::uint32_t>(get_le(raw.subspan(kHeaderSize + len, kCrcSize), 4));
    if (crc32(covered) != stored) {
        return std::unexpected(FrameError::BadCrc);
    }

    return Frame{
        .header = Header{
            .seq   = static_cast<std::uint32_t>(get_le(raw.subspan(2, 4), 4)),
            .ts_ms = get_le(raw.subspan(6, 8), 8),
            .len   = len,
            .kind  = static_cast<Kind>(std::to_integer<std::uint8_t>(raw[16]))
        },
        .payload = raw.subspan(kHeaderSize, len),
        .total   = total
    };
}

} // namespace sf
