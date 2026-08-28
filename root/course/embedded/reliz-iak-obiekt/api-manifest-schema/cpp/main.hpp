#include <cstdint>
#include <cstddef>
#include <array>
#include <span>

inline constexpr std::uint32_t fw_header_magic = 0x46574D46U; // "FWMF"
inline constexpr std::uint32_t fw_header_version = 1U;

#pragma pack(push, 1)
struct alignas(4) FirmwareHeader {
    std::uint32_t magic_word{fw_header_magic};
    std::uint32_t header_version{fw_header_version};
    std::uint32_t target_hw_id{0};
    std::uint8_t  hw_rev_min{0};
    std::uint8_t  hw_rev_max{0};
    std::uint16_t flags{0};
    std::uint8_t  ver_major{0};
    std::uint8_t  ver_minor{0};
    std::uint8_t  ver_patch{0};
    std::uint8_t  ver_pre_flags{0};
    std::uint32_t security_version{0};
    std::uint32_t payload_size{0};
    std::uint32_t load_address{0};
    std::array<std::uint8_t, 32> payload_sha256{};
    std::array<std::uint8_t, 64> signature{};

    [[nodiscard]] constexpr std::span<const std::uint8_t, 64> signed_region() const noexcept {
        return std::span<const std::uint8_t, 64>(reinterpret_cast<const std::uint8_t*>(this), 64);
    }
};
#pragma pack(pop)

static_assert(sizeof(FirmwareHeader) == 128, "FirmwareHeader size must be strictly 128 bytes");
