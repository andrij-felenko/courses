// Кадр оновлення таблиці: SOF(2) | Length(2) | Type(1) | Payload(N*16) | CRC-16(2).
#pragma once

#include "rules/engine.hpp"
#include "rules/schema.hpp"

#include <array>
#include <cstddef>
#include <expected>
#include <span>

namespace rules {

inline constexpr std::byte kSofHi{0xAA};
inline constexpr std::byte kSofLo{0x55};

enum class FrameType : std::uint8_t { RuleTable = 0x01, Ack = 0x06, Nack = 0x15 };

inline constexpr std::size_t kFrameHeader = 5;
inline constexpr std::size_t kFrameCrc    = 2;
inline constexpr std::size_t kMinFrame    = kFrameHeader + kFrameCrc;
inline constexpr std::size_t kMaxFrame    = kFrameHeader + kMaxRules * kDescriptorSize + kFrameCrc;

std::uint16_t crc16Ccitt(std::span<const std::byte> data) noexcept;

std::expected<std::size_t, RuleError> encodeFrame(FrameType type,
                                                  std::span<const std::byte> payload,
                                                  std::span<std::byte> out) noexcept;
std::expected<std::size_t, RuleError> encodeRuleTable(std::span<const RuleDescriptor> table,
                                                      std::span<std::byte> out) noexcept;

// Розбір кадру: синхробайти, довжина, CRC, тип, кратність 16, ліміт місткості.
std::expected<RuleTable, RuleError> decodeRuleTable(std::span<const std::byte> frame) noexcept;

// Відповідь пристрою: ACK з кількістю прийнятих правил або NACK з кодом помилки.
struct Reply {
    std::array<std::byte, kFrameHeader + 1 + kFrameCrc> bytes{};
    std::size_t size{0};
    RuleError   status{RuleError::None};

    std::span<const std::byte> view() const noexcept { return {bytes.data(), size}; }
};

// Повний цикл прийому: розбір → семантика → атомарна фіксація → відповідь.
Reply handleFrame(RuleEngine& engine, std::span<const std::byte> frame) noexcept;

}  // namespace rules
