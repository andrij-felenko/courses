#pragma once

#include <cstddef>
#include <cstdint>
#include <expected>
#include <span>
#include <string_view>
#include <vector>

namespace radio {

inline constexpr std::uint8_t  kPreambleByte  = 0xAA; // 10101010 — суцільні фронти
inline constexpr std::size_t   kPreambleBytes = 4;
inline constexpr std::uint16_t kSyncWord      = 0xD391; // синхрослово CC1101
inline constexpr std::uint32_t kSyncMask      = 0xFFFF; // 16 бітів корелятора
inline constexpr std::size_t   kMaxPayload    = 64;

enum class BuildError {
    EmptyPayload,
    PayloadTooLong,
};

[[nodiscard]] std::string_view describe(BuildError error) noexcept;

// Збирає кадр в ефірному вигляді: преамбула, синхрослово, далі скрембльоване
// тіло — байт довжини, дані й контрольна сума.
[[nodiscard]] std::expected<std::vector<std::uint8_t>, BuildError>
buildFrame(std::span<const std::uint8_t> payload);

} // namespace radio
