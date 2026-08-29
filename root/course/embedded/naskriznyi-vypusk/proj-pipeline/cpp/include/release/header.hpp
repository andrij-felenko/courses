// Формат образу Secure Boot з боку пристрою: розбір заголовка без сирих
// покажчиків і без кодів помилок — межі несе span, провал несе expected.
#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <expected>
#include <span>
#include <string_view>

namespace release {

inline constexpr std::uint32_t kMagic = 0x53424F54u;  // "SBOT"
inline constexpr std::size_t kHeaderSize = 128;
inline constexpr std::size_t kSignedPrefix = 52;      // байти під підписом
inline constexpr std::size_t kDigestSize = 32;
inline constexpr std::size_t kSignatureSize = 64;
inline constexpr std::size_t kPublicKeySize = 65;     // 0x04 || X || Y
inline constexpr std::uint32_t kCurrentHardwareMask = 0x0002u;

enum class Error {
    Truncated,
    Alignment,
    Magic,
    Hardware,
    Rollback,
    PayloadSize,
    Digest,
    Signature,
    Crypto,
};

[[nodiscard]] std::string_view describe(Error error) noexcept;

struct alignas(4) Header {
    std::uint32_t magic;
    std::uint32_t versionPacked;
    std::uint32_t securityCounter;
    std::uint32_t hwMask;
    std::uint32_t payloadSize;
    std::array<std::uint8_t, kDigestSize> payloadSha256;
    std::array<std::uint8_t, kSignatureSize> signature;
    std::array<std::uint8_t, 12> reserved;
};

static_assert(sizeof(Header) == kHeaderSize,
              "заголовок образу мусить бути рівно 128 байтів");

struct Version {
    std::uint8_t major{};
    std::uint8_t minor{};
    std::uint8_t patch{};
};

[[nodiscard]] Version unpackVersion(std::uint32_t packed) noexcept;

// Розібраний образ: заголовок узято копією (128 байтів — дешевше за будь-яку
// гру з часом життя чужого буфера), тіло лишається виглядом у слот.
struct ImageView {
    Header header{};
    std::span<const std::uint8_t> payload{};
};

struct Policy {
    std::uint32_t activeSecurityCounter{};
    std::uint32_t maxPayloadSize{};
    std::uint32_t hardwareMask{kCurrentHardwareMask};
};

[[nodiscard]] std::expected<ImageView, Error> parseHeader(
    std::span<const std::uint8_t> image, const Policy& policy) noexcept;

}  // namespace release
