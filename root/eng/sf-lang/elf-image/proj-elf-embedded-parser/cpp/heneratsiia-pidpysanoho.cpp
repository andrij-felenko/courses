#include <cstdint>
#include <array>
#include <span>
#include <fstream>
#include <string_view>

namespace fota {

inline constexpr std::uint32_t Magic = 0x464F5441U; // 'FOTA'

#pragma pack(push, 1)
struct Header {
    std::uint32_t magic{Magic};
    std::uint32_t version_major{1};
    std::uint32_t version_minor{0};
    std::uint32_t version_patch{0};
    std::uint32_t target_hw_id{0x0042};
    std::uint32_t entry_point{0};
    std::uint32_t flash_target_lma{0x08000000};
    std::uint32_t payload_size{0};
    std::uint32_t payload_crc32{0};
    std::array<std::uint8_t, 32> sha256_hash{};
    std::array<std::uint8_t, 64> signature{};
};
#pragma pack(pop)

bool create_package(std::span<const std::uint8_t> binary_payload,
                    std::uint32_t entry_point,
                    std::uint32_t flash_lma,
                    std::string_view output_path) {
    if (binary_payload.empty()) return false;

    Header header{};
    header.entry_point = entry_point;
    header.flash_target_lma = flash_lma;
    header.payload_size = static_cast<std::uint32_t>(binary_payload.size());
    header.payload_crc32 = integrity::calculate_crc32(binary_payload);

    std::ofstream out(std::string(output_path), std::ios::binary);
    if (!out) return false;

    out.write(reinterpret_cast<const char*>(&header), sizeof(Header));
    out.write(reinterpret_cast<const char*>(binary_payload.data()), binary_payload.size());

    return true;
}

} // namespace fota
