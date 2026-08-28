#include <cstdint>
#include <string_view>
#include <span>

/* Безпечна C++ типізація детермінованих метаданих прошивки */
struct alignas(4) FirmwareMeta {
    uint32_t magic;
    uint32_t build_timestamp;
    char     git_commit[16];
    char     toolchain_id[16];
    uint32_t image_crc32;

    static constexpr uint32_t ExpectedMagic = 0x544F4F4CU; /* 'TOOL' */

    [[nodiscard]] constexpr bool isValid() const noexcept {
        return (magic == ExpectedMagic) && (build_timestamp != 0U);
    }

    [[nodiscard]] constexpr std::string_view getGitCommit() const noexcept {
        return std::string_view(git_commit, 16);
    }
};

#ifndef SOURCE_DATE_EPOCH
#define SOURCE_DATE_EPOCH 0U
#endif

[[gnu::section(".meta"), gnu::used]]
constexpr FirmwareMeta g_firmware_meta{
    .magic           = FirmwareMeta::ExpectedMagic,
    .build_timestamp = static_cast<uint32_t>(SOURCE_DATE_EPOCH),
    .git_commit      = {'a','1','b','2','c','3','d','4','e','5','f','6','0','7','1','8'},
    .toolchain_id    = {'g','c','c','-','1','3','.','2','.','a','r','m', 0, 0, 0, 0},
    .image_crc32     = 0xDEADBEEFU
};

static_assert(g_firmware_meta.isValid(), "Metadata structure must be valid at compile time");

int verify_metadata(std::span<const uint8_t> meta_bytes) noexcept {
    if (meta_bytes.size() < sizeof(FirmwareMeta)) {
        return -1;
    }
    const auto* meta = reinterpret_cast<const FirmwareMeta*>(meta_bytes.data());
    return meta->isValid() ? 0 : -2;
}
