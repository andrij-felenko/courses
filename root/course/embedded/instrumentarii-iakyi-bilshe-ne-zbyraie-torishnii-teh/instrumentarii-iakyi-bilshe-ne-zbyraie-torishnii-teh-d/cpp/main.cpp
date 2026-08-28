#include <cstdint>
#include <string_view>
#include <span>
#include <array>

/* Безпечна C++ структура метаданих збірки з перевірками часу компіляції */
struct alignas(4) ReleaseMetadata {
    uint32_t magic;
    uint32_t build_timestamp;
    std::array<uint8_t, 20> git_hash;
    std::array<uint8_t, 8>  toolchain_hash;
    uint32_t firmware_crc32;
    uint32_t reserved;

    static constexpr uint32_t MagicSignature = 0x4D4C4552U; /* 'RELM' */

    [[nodiscard]] constexpr bool isValid() const noexcept {
        return (magic == MagicSignature) && (build_timestamp != 0U);
    }

    [[nodiscard]] constexpr std::span<const uint8_t, 20> getGitHash() const noexcept {
        return std::span<const uint8_t, 20>(git_hash);
    }
};

#ifndef SOURCE_DATE_EPOCH
#define SOURCE_DATE_EPOCH 0U
#endif

[[gnu::section(".meta_header"), gnu::used]]
constexpr ReleaseMetadata g_release_meta{
    .magic           = ReleaseMetadata::MagicSignature,
    .build_timestamp = static_cast<uint32_t>(SOURCE_DATE_EPOCH),
    .git_hash        = {0xa1, 0xb2, 0xc3, 0xd4, 0xe5, 0xf6, 0x07, 0x18, 
                        0x29, 0x3a, 0x4b, 0x5c, 0x6d, 0x7e, 0x8f, 0x90, 
                        0x12, 0x34, 0x56, 0x78},
    .toolchain_hash  = {0x3f, 0xbc, 0x63, 0x21, 0x67, 0x42, 0x4a, 0x6d},
    .firmware_crc32  = 0x9B8C7D6EU,
    .reserved        = 0U
};

static_assert(g_release_meta.isValid(), "Release metadata must satisfy invariants at compile time");

[[nodiscard]] bool validate_firmware_header(std::span<const uint8_t> memory_region) noexcept {
    if (memory_region.size() < sizeof(ReleaseMetadata)) {
        return false;
    }
    const auto* meta = reinterpret_cast<const ReleaseMetadata*>(memory_region.data());
    return meta->isValid();
}
