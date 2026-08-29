#pragma once

#include <array>
#include <bit>
#include <compare>
#include <cstddef>
#include <cstdint>
#include <span>
#include <string_view>

namespace fw {

/* 0x46574D46 — це ASCII 'F','W','M','F' (Firmware Manifest), виписані від
   старшого байта до молодшого. */
inline constexpr std::uint32_t header_magic = 0x46574D46u;

/* Версія формату САМОГО дескриптора: завантажувач приймає лише ту, яку
   вміє читати, інакше поля означали б не те, що він думає. */
inline constexpr std::uint32_t header_format_version = 1u;

/* Підпис накладається рівно на перші 64 байти. Геш тіла сидить усередині
   них, тому підпис над заголовком засвідчує й увесь бінарник. */
inline constexpr std::size_t signed_prefix_size = 64;
inline constexpr std::size_t descriptor_size = 128;

using Digest    = std::array<std::byte, 32>;
using Signature = std::array<std::byte, 64>;
using PublicKey = std::span<const std::byte, 32>;

struct Version {
    std::uint8_t major{};
    std::uint8_t minor{};
    std::uint8_t patch{};
    std::uint8_t pre_flags{};

    /* Порядок полів збігається з порядком старшинства SemVer, тож
       порівняння за замовчуванням дає саме те, що треба. */
    friend constexpr auto operator<=>(const Version&, const Version&) = default;
};

enum class VerifyError : std::uint8_t {
    BadMagic             = 1,
    HardwareIncompatible = 2,
    Rollback             = 3,
    BadGeometry          = 4,
    NoRootKey            = 5,
    BadSignature         = 6,
    HashMismatch         = 7,
    FlashIo              = 8
};

/* Символьне ім'я — те саме, яке виходить у діагностичний протокол
   і в журнал сервера оновлень. */
[[nodiscard]] constexpr std::string_view describe(VerifyError error) noexcept
{
    switch (error) {
    case VerifyError::BadMagic:             return "ERR_FW_BAD_MAGIC";
    case VerifyError::HardwareIncompatible: return "ERR_FW_HW_INCOMPATIBLE";
    case VerifyError::Rollback:             return "ERR_FW_ROLLBACK_DETECTED";
    case VerifyError::BadGeometry:          return "ERR_FW_BAD_GEOMETRY";
    case VerifyError::NoRootKey:            return "ERR_FW_NO_ROOT_KEY";
    case VerifyError::BadSignature:         return "ERR_FW_INVALID_SIGNATURE";
    case VerifyError::HashMismatch:         return "ERR_FW_HASH_MISMATCH";
    case VerifyError::FlashIo:              return "ERR_FW_FLASH_IO";
    }
    return "ERR_FW_UNKNOWN";
}

/* Це не «зручна структура в пам'яті», а розкладка на носії: жодного
   вирівнювального байта компілятор дописати не має права. */
#pragma pack(push, 1)
struct Descriptor {
    std::uint32_t magic_word;        // 0x00
    std::uint32_t format_version;    // 0x04
    std::uint32_t target_hw_id;      // 0x08  код виробу, напр. 0x0000A110
    std::uint8_t  hw_rev_min;        // 0x0C
    std::uint8_t  hw_rev_max;        // 0x0D
    std::uint16_t flags;             // 0x0E  зарезервовано, має бути 0
    Version       version;           // 0x10
    std::uint32_t security_version;  // 0x14  монотонний індекс anti-rollback
    std::uint32_t payload_size;      // 0x18
    std::uint32_t load_address;      // 0x1C
    Digest        payload_sha256;    // 0x20
    Signature     signature;         // 0x40  Ed25519 над 0x00..0x3F

    [[nodiscard]] bool magic_ok() const noexcept
    {
        return magic_word == header_magic && format_version == header_format_version;
    }

    [[nodiscard]] constexpr bool accepts_revision(std::uint8_t revision) const noexcept
    {
        return revision >= hw_rev_min && revision <= hw_rev_max;
    }

    /* Підписаний префікс як типізований вид на власні байти: довжина 64
       зашита в тип, тож переплутати межу підпису неможливо. */
    [[nodiscard]] std::span<const std::byte, signed_prefix_size> signed_prefix() const noexcept
    {
        return std::span<const std::byte, signed_prefix_size>{
            reinterpret_cast<const std::byte*>(this), signed_prefix_size};
    }
};
#pragma pack(pop)

static_assert(sizeof(Descriptor) == descriptor_size,
              "дескриптор мусить займати рівно 128 байтів");
static_assert(offsetof(Descriptor, payload_sha256) == 32,
              "геш образу стоїть за зсувом 0x20");
static_assert(offsetof(Descriptor, signature) == signed_prefix_size,
              "підпис починається рівно там, де закінчується підписана частина");
static_assert(std::endian::native == std::endian::little,
              "розкладка дескриптора описана в little-endian");

}  // namespace fw
