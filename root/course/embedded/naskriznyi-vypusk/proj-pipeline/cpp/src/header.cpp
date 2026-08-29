#include "release/header.hpp"

#include <bit>
#include <cstring>

namespace release {
namespace {

// Заголовок написано little-endian; на Cortex-M і на хості це рідний
// порядок, але покладатися на це мовчки не можна.
[[nodiscard]] std::uint32_t readU32(std::span<const std::uint8_t> bytes) noexcept
{
    std::uint32_t value = static_cast<std::uint32_t>(bytes[0])
                        | (static_cast<std::uint32_t>(bytes[1]) << 8)
                        | (static_cast<std::uint32_t>(bytes[2]) << 16)
                        | (static_cast<std::uint32_t>(bytes[3]) << 24);
    return value;
}

template <std::size_t N>
void copyArray(std::span<const std::uint8_t> src, std::array<std::uint8_t, N>& dst) noexcept
{
    std::memcpy(dst.data(), src.data(), N);
}

}  // namespace

std::string_view describe(Error error) noexcept
{
    switch (error) {
    case Error::Truncated:   return "образ обірваний";
    case Error::Alignment:   return "буфер не вирівняний на 4 байти";
    case Error::Magic:       return "чуже магічне число";
    case Error::Hardware:    return "прошивка не для цієї ревізії плати";
    case Error::Rollback:    return "відкат на застарілу версію";
    case Error::PayloadSize: return "тіло не влазить у слот застосунку";
    case Error::Digest:      return "хеш тіла не збігся";
    case Error::Signature:   return "підпис не від кореня довіри";
    case Error::Crypto:      return "збій криптографічного модуля";
    }
    return "невідомий стан";
}

Version unpackVersion(std::uint32_t packed) noexcept
{
    return Version{
        static_cast<std::uint8_t>((packed >> 24) & 0xFFu),
        static_cast<std::uint8_t>((packed >> 16) & 0xFFu),
        static_cast<std::uint8_t>((packed >> 8) & 0xFFu),
    };
}

std::expected<ImageView, Error> parseHeader(std::span<const std::uint8_t> image,
                                            const Policy& policy) noexcept
{
    if (image.size() < kHeaderSize) {
        return std::unexpected(Error::Truncated);
    }

    // Слот завантаження у Flash пристрою вирівняний; перевіряємо явно, бо
    // на хостовому стенді буфер може приїхати звідки завгодно.
    if ((std::bit_cast<std::uintptr_t>(image.data()) & 0x3u) != 0u) {
        return std::unexpected(Error::Alignment);
    }

    ImageView view{};
    Header& hdr = view.header;
    // Копіюємо поле за полем замість reinterpret_cast: так немає ні
    // припущень про розкладку, ні запуску життя чужого об'єкта в буфері.
    hdr.magic = readU32(image.subspan(0, 4));
    hdr.versionPacked = readU32(image.subspan(4, 4));
    hdr.securityCounter = readU32(image.subspan(8, 4));
    hdr.hwMask = readU32(image.subspan(12, 4));
    hdr.payloadSize = readU32(image.subspan(16, 4));
    copyArray(image.subspan(20, kDigestSize), hdr.payloadSha256);
    copyArray(image.subspan(52, kSignatureSize), hdr.signature);
    copyArray(image.subspan(116, 12), hdr.reserved);

    if (hdr.magic != kMagic) {
        return std::unexpected(Error::Magic);
    }
    if ((hdr.hwMask & policy.hardwareMask) == 0u) {
        return std::unexpected(Error::Hardware);
    }
    if (hdr.securityCounter < policy.activeSecurityCounter) {
        return std::unexpected(Error::Rollback);
    }
    if (hdr.payloadSize == 0u || hdr.payloadSize > policy.maxPayloadSize) {
        return std::unexpected(Error::PayloadSize);
    }
    if (image.size() - kHeaderSize < hdr.payloadSize) {
        return std::unexpected(Error::Truncated);
    }

    view.payload = image.subspan(kHeaderSize, hdr.payloadSize);
    return view;
}

}  // namespace release
