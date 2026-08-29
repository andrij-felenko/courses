#include "manifest.hpp"

#include <algorithm>

#include "crc32.hpp"

namespace boot {
namespace {

// Явне читання little-endian слова: єдине місце, де знання про порядок байтів
// на носії живе в коді.
[[nodiscard]] std::uint32_t readU32(std::span<const std::uint8_t> bytes,
                                    std::size_t offset) noexcept
{
    return static_cast<std::uint32_t>(bytes[offset]) |
           (static_cast<std::uint32_t>(bytes[offset + 1]) << 8) |
           (static_cast<std::uint32_t>(bytes[offset + 2]) << 16) |
           (static_cast<std::uint32_t>(bytes[offset + 3]) << 24);
}

} // namespace

std::expected<Manifest, Status> Manifest::parse(std::span<const std::uint8_t> slot) noexcept
{
    if (slot.size() < kManifestSize) {
        return std::unexpected(Status::BadImageLayout);
    }

    Manifest manifest;
    // Копіюємо заголовок у SRAM і далі дивимось лише на копію: Flash під час
    // перевірки може переписати контролер оновлення, і перевірене значення
    // розійшлося б із використаним.
    std::ranges::copy(slot.first(kManifestSize), manifest.raw_.begin());

    const std::span<const std::uint8_t> header{manifest.raw_};

    if (readU32(header, 0) != kManifestMagic) {
        return std::unexpected(Status::InvalidMagic);
    }

    const std::uint32_t storedCrc = readU32(header, 4);
    if (crc32(header.subspan(8)) != storedCrc) {
        return std::unexpected(Status::InvalidMagic);
    }

    manifest.payloadLength_ = readU32(header, 8);
    manifest.loadAddress_ = readU32(header, 12);
    manifest.securityVersion_ = readU32(header, 16);
    manifest.keySlotIndex_ = header[20];

    if (manifest.keySlotIndex_ >= kKeySlots) {
        return std::unexpected(Status::InvalidSlot);
    }
    // Резервні байти — місце під майбутні прапорці. Невідоме значення означає
    // формат, якого ця версія завантажувача не розуміє.
    if (header[21] != 0 || header[22] != 0 || header[23] != 0) {
        return std::unexpected(Status::InvalidMagic);
    }

    std::ranges::copy(header.subspan(24, kPublicKeySize), manifest.publicKey_.begin());
    std::ranges::copy(header.subspan(88, kSignatureSize), manifest.signature_.begin());

    if (manifest.payloadLength_ == 0 ||
        manifest.payloadLength_ > slot.size() - kManifestSize) {
        return std::unexpected(Status::BadImageLayout);
    }

    return manifest;
}

} // namespace boot
