#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <expected>
#include <span>

#include "boot_status.hpp"

namespace boot {

inline constexpr std::uint32_t kManifestMagic = 0x5346574DU; // "SFWM"
inline constexpr std::size_t kKeySlots = 4;
inline constexpr std::size_t kDigestSize = 32;
inline constexpr std::size_t kPublicKeySize = 64;   // ECDSA P-256: X||Y
inline constexpr std::size_t kSignatureSize = 64;   // ECDSA P-256: r||s
inline constexpr std::size_t kManifestSize = 152;
inline constexpr std::size_t kSignedHeaderSize = 88; // заголовок без поля підпису

using Digest = std::array<std::uint8_t, kDigestSize>;
using PublicKey = std::array<std::uint8_t, kPublicKeySize>;
using Signature = std::array<std::uint8_t, kSignatureSize>;

// Заголовок образу. Байти з Flash не накладаємо на структуру вказівником:
// розбираємо поле за полем із явним порядком байтів. Компілятор тоді нічого
// не «вирівнює» за нашою спиною, а розкладка на носії лишається однією —
// тією, що описана в parse().
class Manifest {
public:
    [[nodiscard]] static std::expected<Manifest, Status>
    parse(std::span<const std::uint8_t> slot) noexcept;

    [[nodiscard]] std::uint32_t payloadLength() const noexcept { return payloadLength_; }
    [[nodiscard]] std::uint32_t loadAddress() const noexcept { return loadAddress_; }
    [[nodiscard]] std::uint32_t securityVersion() const noexcept { return securityVersion_; }
    [[nodiscard]] std::uint8_t keySlotIndex() const noexcept { return keySlotIndex_; }

    [[nodiscard]] std::span<const std::uint8_t, kPublicKeySize> publicKey() const noexcept
    {
        return publicKey_;
    }

    [[nodiscard]] std::span<const std::uint8_t, kSignatureSize> signature() const noexcept
    {
        return signature_;
    }

    // Байти заголовка, які накриває підпис (усе, крім самого підпису).
    [[nodiscard]] std::span<const std::uint8_t> signedHeader() const noexcept
    {
        return std::span<const std::uint8_t>{raw_}.first(kSignedHeaderSize);
    }

    // Тіло прошивки всередині переданого розділу.
    [[nodiscard]] std::span<const std::uint8_t>
    payload(std::span<const std::uint8_t> slot) const noexcept
    {
        return slot.subspan(kManifestSize, payloadLength_);
    }

private:
    Manifest() = default;

    std::array<std::uint8_t, kManifestSize> raw_{};
    std::uint32_t payloadLength_{};
    std::uint32_t loadAddress_{};
    std::uint32_t securityVersion_{};
    std::uint8_t keySlotIndex_{};
    PublicKey publicKey_{};
    Signature signature_{};
};

} // namespace boot
