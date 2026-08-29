#include "edge/telemetry_frame.hpp"

#include <bit>
#include <cmath>

namespace edge {
namespace {

constexpr std::uint8_t frame_magic   = 0x7E;
constexpr std::uint8_t frame_version = 1;

/// Курсор запису поверх чужого буфера. Тримає span і позицію разом,
/// тож розсинхронізувати вказівник із залишком місця нема як.
class Writer {
public:
    explicit constexpr Writer(std::span<std::byte> out) noexcept : out_{out} {}

    constexpr void u8(std::uint8_t v) noexcept { out_[pos_++] = std::byte{v}; }

    constexpr void u16(std::uint16_t v) noexcept
    {
        u8(static_cast<std::uint8_t>(v & 0xFF));
        u8(static_cast<std::uint8_t>(v >> 8));
    }

    constexpr void u32(std::uint32_t v) noexcept
    {
        u16(static_cast<std::uint16_t>(v & 0xFFFF));
        u16(static_cast<std::uint16_t>(v >> 16));
    }

    void f32(float v) noexcept
    {
        // Не-скінченне значення в ефір не пускаємо: розбирач на тому боці
        // майже напевно на ньому впаде, а прапорець відмови вже в заголовку.
        if (!std::isfinite(v)) {
            v = 0.0f;
        }
        u32(std::bit_cast<std::uint32_t>(v));   // без memcpy і без гри з aliasing
    }

    [[nodiscard]] constexpr std::span<const std::byte> written() const noexcept
    {
        return out_.first(pos_);
    }

private:
    std::span<std::byte> out_;
    std::size_t pos_{0};
};

std::uint16_t z_to_q8_8(float z) noexcept
{
    if (!std::isfinite(z) || z >= 255.99f) {
        return 0xFFFF;   // насичення: «дуже далеко», точність тут ні до чого
    }
    if (z <= 0.0f) {
        return 0;
    }
    return static_cast<std::uint16_t>(z * 256.0f + 0.5f);
}

std::int16_t to_fixed(float sample, float mean) noexcept
{
    if (!std::isfinite(sample) || !std::isfinite(mean)) {
        return snapshot_invalid;
    }
    const float scaled = (sample - mean) * 100.0f;
    if (scaled >= 32767.0f) {
        return 32767;
    }
    if (scaled <= -32767.0f) {
        return -32767;   // -32768 зарезервовано під «вибірка невалідна»
    }
    return static_cast<std::int16_t>(scaled >= 0.0f ? scaled + 0.5f : scaled - 0.5f);
}

}  // namespace

std::uint16_t crc16_ccitt(std::span<const std::byte> data) noexcept
{
    // CRC-16/CCITT-FALSE: поліном 0x1021, початок 0xFFFF, без відображення.
    // Побітово: таблиця на 512 байт не окупається на кадрі менш ніж у 90 байт.
    std::uint16_t crc = 0xFFFF;
    for (const std::byte b : data) {
        crc ^= static_cast<std::uint16_t>(std::to_integer<std::uint8_t>(b) << 8);
        for (int bit = 0; bit < 8; ++bit) {
            crc = (crc & 0x8000) ? static_cast<std::uint16_t>((crc << 1) ^ 0x1021)
                                 : static_cast<std::uint16_t>(crc << 1);
        }
    }
    return crc;
}

std::optional<std::span<const std::byte>>
encode(const Report& report, std::span<const float> snapshot, std::span<std::byte> out) noexcept
{
    if (snapshot.size() > snapshot_depth) {
        snapshot = snapshot.first(snapshot_depth);
    }

    const std::size_t needed = frame_header_size + 2 * snapshot.size() + 2;
    if (out.size() < needed) {
        return std::nullopt;
    }

    Writer w{out};
    w.u8(frame_magic);
    w.u8(static_cast<std::uint8_t>((frame_version << 4) | (report.sensor_fault ? 0x1 : 0x0)));
    w.u8(static_cast<std::uint8_t>(report.action));
    w.u32(report.timestamp.count());
    w.f32(report.value);
    w.f32(report.mean);
    w.f32(report.stddev);
    w.u16(z_to_q8_8(report.z));
    w.u8(static_cast<std::uint8_t>(snapshot.size()));

    for (const float sample : snapshot) {
        w.u16(static_cast<std::uint16_t>(to_fixed(sample, report.mean)));
    }

    w.u16(crc16_ccitt(w.written()));
    return w.written();
}

}  // namespace edge
