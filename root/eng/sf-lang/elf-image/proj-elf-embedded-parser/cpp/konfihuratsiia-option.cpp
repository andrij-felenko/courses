#include <cstdint>
#include <span>
#include <optional>

namespace options {

inline constexpr std::uint32_t OptBytesBase = 0x1FFFC000U;

struct OptionBytesConfig {
    std::uint8_t rdp_level;
    std::uint8_t user_options;
    std::uint16_t write_protection_mask;
};

[[nodiscard]] std::optional<OptionBytesConfig> extract_config(
    std::span<const elf::ProgramHeader32> segments,
    std::span<const std::uint8_t> raw_file) noexcept {
    for (const auto& seg : segments) {
        if (seg.paddr == OptBytesBase && seg.file_size >= sizeof(OptionBytesConfig)) {
            if (seg.offset + sizeof(OptionBytesConfig) <= raw_file.size()) {
                const auto* ptr = raw_file.data() + seg.offset;
                return OptionBytesConfig{
                    .rdp_level = ptr[0],
                    .user_options = ptr[1],
                    .write_protection_mask = static_cast<std::uint16_t>(ptr[2] | (ptr[3] << 8))
                };
            }
        }
    }
    return std::nullopt;
}

} // namespace options
