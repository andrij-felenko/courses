// frame.hpp — формат кадру на носії.
//
//   0..1   magic 0xAA55 · 2 type · 3 flags(пріоритет)
//   4..7   seq · 8..15 timestamp_ms · 16..17 payload_len · 18..19 reserved
//   20..   payload · далі crc32(header+payload) · далі 0xFF до межі 4 байтів
//
// Структуру у флеш не пишемо байтовою копією: розкладка полів у пам'яті
// залежить від компілятора й ключів, а формат на носії мусить пережити
// зміну і того, і того. Серіалізація явна, через шаблон put_le/get_le.
#pragma once

#include <algorithm>
#include <concepts>
#include <cstddef>
#include <cstdint>
#include <optional>
#include <ranges>
#include <span>
#include <utility>

#include "sfq/crc32.hpp"

namespace sfq {

inline constexpr std::size_t kHeaderSize = 20;
inline constexpr std::size_t kCrcSize = 4;
inline constexpr std::size_t kAlign = 4;
inline constexpr std::size_t kMaxPayload = 512;
inline constexpr std::size_t kRecordMax = kHeaderSize + kMaxPayload + kCrcSize;  // 536
inline constexpr std::uint16_t kMagic = 0xAA55u;

enum class Priority : std::uint8_t {
    Low = 0,     // високочастотна телеметрія — витісняється першою
    Normal = 1,  // періодичний статус
    High = 2,    // аварії — заради них витісняють історію
};

enum class RecordType : std::uint8_t {
    Telemetry = 1,
    Status = 2,
    Alarm = 3,
};

struct FrameHeader {
    RecordType type{RecordType::Telemetry};
    Priority priority{Priority::Normal};
    std::uint32_t seq{};
    std::uint64_t timestamp_ms{};
    std::uint16_t payload_len{};
};

[[nodiscard]] constexpr std::size_t frame_stride(std::uint16_t payload_len) noexcept
{
    const std::size_t raw = kHeaderSize + payload_len + kCrcSize;
    return (raw + (kAlign - 1)) & ~(kAlign - 1);
}

namespace detail {

template <std::unsigned_integral T>
constexpr void put_le(std::span<std::byte> dst, T value) noexcept
{
    for (std::size_t i = 0; i < sizeof(T); ++i) {
        dst[i] = static_cast<std::byte>((value >> (8 * i)) & 0xFFu);
    }
}

template <std::unsigned_integral T>
[[nodiscard]] constexpr T get_le(std::span<const std::byte> src) noexcept
{
    T value{};
    for (std::size_t i = 0; i < sizeof(T); ++i) {
        value |= static_cast<T>(std::to_integer<std::uint8_t>(src[i])) << (8 * i);
    }
    return value;
}

}  // namespace detail

// Пакує кадр у dst (щонайменше kRecordMax байтів) і повертає stride.
[[nodiscard]] inline std::size_t frame_pack(std::span<std::byte> dst, const FrameHeader& hdr,
                                            std::span<const std::byte> payload) noexcept
{
    const std::size_t body = kHeaderSize + payload.size();
    const std::size_t stride = frame_stride(static_cast<std::uint16_t>(payload.size()));

    detail::put_le<std::uint16_t>(dst.subspan(0), kMagic);
    dst[2] = static_cast<std::byte>(std::to_underlying(hdr.type));
    dst[3] = static_cast<std::byte>(std::to_underlying(hdr.priority) & 0x03u);
    detail::put_le<std::uint32_t>(dst.subspan(4), hdr.seq);
    detail::put_le<std::uint64_t>(dst.subspan(8), hdr.timestamp_ms);
    detail::put_le<std::uint16_t>(dst.subspan(16), static_cast<std::uint16_t>(payload.size()));
    detail::put_le<std::uint16_t>(dst.subspan(18), 0u);

    std::ranges::copy(payload, dst.begin() + kHeaderSize);
    detail::put_le<std::uint32_t>(dst.subspan(body), crc32(dst.first(body)));

    // Вирівнювання лишаємо стертим: у NOR одиниця — це «нічого не робили».
    std::ranges::fill(dst.subspan(body + kCrcSize, stride - body - kCrcSize), std::byte{0xFF});
    return stride;
}

// nullopt — це не кадр: або чужа преамбула, або немислима довжина.
[[nodiscard]] inline std::optional<FrameHeader> frame_parse(std::span<const std::byte> src) noexcept
{
    if (src.size() < kHeaderSize || detail::get_le<std::uint16_t>(src) != kMagic) {
        return std::nullopt;
    }

    const auto len = detail::get_le<std::uint16_t>(src.subspan(16));
    if (len == 0 || len > kMaxPayload) {
        return std::nullopt;
    }

    return FrameHeader{
        .type = static_cast<RecordType>(std::to_integer<std::uint8_t>(src[2])),
        .priority = static_cast<Priority>(std::to_integer<std::uint8_t>(src[3]) & 0x03u),
        .seq = detail::get_le<std::uint32_t>(src.subspan(4)),
        .timestamp_ms = detail::get_le<std::uint64_t>(src.subspan(8)),
        .payload_len = len,
    };
}

[[nodiscard]] inline bool frame_crc_ok(std::span<const std::byte> record,
                                       std::uint16_t payload_len) noexcept
{
    const std::size_t body = kHeaderSize + payload_len;
    return crc32(record.first(body)) == detail::get_le<std::uint32_t>(record.subspan(body));
}

// Стерта область — межа записаного, а не пошкодження.
[[nodiscard]] inline bool is_blank(std::span<const std::byte> data) noexcept
{
    return std::ranges::all_of(data, [](std::byte b) { return b == std::byte{0xFF}; });
}

}  // namespace sfq
