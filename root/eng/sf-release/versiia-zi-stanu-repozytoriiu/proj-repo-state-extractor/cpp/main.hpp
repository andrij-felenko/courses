/* Згенеровано автоматично: не редагувати вручну */
#pragma once

#include <cstdint>
#include <string_view>
#include <array>
#include <span>

namespace build_metadata {

inline constexpr std::uint32_t magic_signature = 0x56455253U; // 'VERS'
inline constexpr std::uint16_t struct_version_v1 = 1U;

enum class BuildFlags : std::uint16_t {
    None       = 0,
    Dirty      = 1U << 0,
    Debug      = 1U << 1,
    Prerelease = 1U << 2,
    Ci         = 1U << 3
};

constexpr BuildFlags operator|(BuildFlags a, BuildFlags b) noexcept {
    return static_cast<BuildFlags>(static_cast<std::uint16_t>(a) | static_cast<std::uint16_t>(b));
}

constexpr bool has_flag(BuildFlags value, BuildFlags flag) noexcept {
    return (static_cast<std::uint16_t>(value) & static_cast<std::uint16_t>(flag)) != 0;
}

#pragma pack(push, 4)
struct VersionInfo {
    std::uint32_t magic;
    std::uint16_t struct_version;
    BuildFlags    flags;
    std::uint16_t major;
    std::uint16_t minor;
    std::uint16_t patch;
    std::uint16_t reserved;
    std::uint32_t commit_count;
    std::array<char, 8> git_sha_short;
    std::uint64_t timestamp;
    std::array<char, 32> tag_name;
    std::uint32_t crc32;

    [[nodiscard]] constexpr bool is_dirty() const noexcept {
        return has_flag(flags, BuildFlags::Dirty);
    }

    [[nodiscard]] constexpr bool is_official_release() const noexcept {
        return !is_dirty() && !has_flag(flags, BuildFlags::Debug | BuildFlags::Prerelease);
    }

    [[nodiscard]] std::string_view tag() const noexcept {
        return std::string_view(tag_name.data());
    }

    [[nodiscard]] std::string_view sha() const noexcept {
        return std::string_view(git_sha_short.data(), 8);
    }
};
#pragma pack(pop)

#if defined(__GNUC__) || defined(__clang__)
[[gnu::section(".version_header"), gnu::used]]
#endif
extern const VersionInfo active_version_descriptor;

} // namespace build_metadata
