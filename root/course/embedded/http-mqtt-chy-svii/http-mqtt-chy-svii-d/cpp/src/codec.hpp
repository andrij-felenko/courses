// codec.hpp — збирання й розбирання кадру.
//
// Помилку повертає std::expected, а не -1 з errno: викликач не може
// випадково пропустити невдачу, бо результат позначено [[nodiscard]].
#pragma once

#include <cstddef>
#include <cstdint>
#include <expected>
#include <span>
#include <string_view>

#include "frame.hpp"

namespace telemetry {

[[nodiscard]] std::uint16_t crc16(std::span<const std::byte> data) noexcept;

// Складає кадр у наданий буфер і повертає рівно ту його частину, що пішла в діло.
[[nodiscard]] std::expected<std::span<const std::byte>, FrameError>
encodeTelemetry(const Sample& sample, std::uint16_t seq,
                std::span<std::byte> out) noexcept;

[[nodiscard]] std::expected<Packet, FrameError>
decodeTelemetry(std::span<const std::byte> raw) noexcept;

[[nodiscard]] std::expected<std::span<const std::byte>, FrameError>
encodeAck(std::uint16_t seq, std::span<std::byte> out) noexcept;

[[nodiscard]] std::expected<std::uint16_t, FrameError>
decodeAck(std::span<const std::byte> raw) noexcept;

[[nodiscard]] std::string_view describe(FrameError error) noexcept;

}  // namespace telemetry
