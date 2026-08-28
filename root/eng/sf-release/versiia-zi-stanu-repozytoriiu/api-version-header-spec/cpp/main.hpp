#pragma once

#include <cstdint>
#include <span>
#include <string_view>
#include <optional>
#include <array>

namespace firmware_abi {

inline constexpr std::uint32_t magic_value = 0x56455253U;

#pragma pack(push, 4)
struct VersionDescriptor {
    std::uint32_t magic;
    std::uint16_t struct_version;
    std::uint16_t flags;
    std::uint16_t major;
    std::uint16_t minor;
    std::uint16_t patch;
    std::uint16_t reserved;
    std::uint32_t commit_count;
    std::array<char, 8> git_sha_short;
    std::uint64_t timestamp;
    std::array<char, 32> tag_name;
    std::uint32_t crc32;
};
#pragma pack(pop)

class VersionValidator {
public:
    static constexpr std::uint32_t compute_crc32(std::span<const std::uint8_t> data) noexcept {
        std::uint32_t crc = 0xFFFFFFFFU;
        for (std::uint8_t b : data) {
            crc ^= b;
            for (int j = 0; j < 8; ++j) {
                crc = (crc >> 1) ^ (0xEDB88320U & -(crc & 1U));
            }
        }
        return ~crc;
    }

    [[nodiscard]] static bool is_valid(const VersionDescriptor& desc) noexcept {
        if (desc.magic != magic_value || desc.struct_version != 1U) {
            return false;
        }
        auto payload = std::span<const std::uint8_t>(
            reinterpret_cast<const std::uint8_t*>(&desc),
            sizeof(VersionDescriptor) - sizeof(desc.crc32)
        );
        return desc.crc32 == compute_crc32(payload);
    }
};

} // namespace firmware_abi
