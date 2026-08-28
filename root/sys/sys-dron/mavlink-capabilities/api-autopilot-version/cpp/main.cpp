#include <cstdint>
#include <string>
#include <string_view>
#include <array>
#include <format>
#include <span>

enum class ReleaseType : uint8_t {
    Dev      = 0,
    Alpha    = 64,
    Beta     = 128,
    Rc       = 192,
    Official = 255
};

class AutopilotVersionDecoder {
public:
    struct VersionInfo {
        uint8_t major{0};
        uint8_t minor{0};
        uint8_t patch{0};
        ReleaseType type{ReleaseType::Dev};

        [[nodiscard]] std::string to_string() const {
            std::string_view suffix;
            switch (type) {
                case ReleaseType::Dev:      suffix = "-dev"; break;
                case ReleaseType::Alpha:    suffix = "-alpha"; break;
                case ReleaseType::Beta:     suffix = "-beta"; break;
                case ReleaseType::Rc:       suffix = "-rc"; break;
                case ReleaseType::Official: suffix = ""; break;
            }
            return std::format("v{}.{}.{}{}", major, minor, patch, suffix);
        }
    };

    [[nodiscard]] static VersionInfo decode_version(uint32_t raw) noexcept {
        return {
            .major = static_cast<uint8_t>((raw >> 24) & 0xFF),
            .minor = static_cast<uint8_t>((raw >> 16) & 0xFF),
            .patch = static_cast<uint8_t>((raw >> 8) & 0xFF),
            .type  = static_cast<ReleaseType>(raw & 0xFF)
        };
    }

    [[nodiscard]] static std::string format_git_hash(std::span<const uint8_t, 8> custom_ver) {
        std::string hash_str;
        hash_str.reserve(16);
        for (uint8_t b : custom_ver) {
            hash_str += std::format("{:02x}", b);
        }
        return hash_str;
    }

    [[nodiscard]] static std::string format_uid2(std::span<const uint8_t, 18> uid_bytes) {
        std::string out;
        out.reserve(36);
        for (size_t i = 0; i < uid_bytes.size(); ++i) {
            out += std::format("{:02X}", uid_bytes[i]);
            if (i + 1 < uid_bytes.size() && (i == 3 || i == 5 || i == 7 || i == 9)) {
                out += '-';
            }
        }
        return out;
    }
};
