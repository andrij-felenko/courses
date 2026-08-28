#include <cstdint>
#include <string>
#include <string_view>
#include <format>
#include <span>

enum class FirmwareType : uint8_t {
    Dev      = 0,
    Alpha    = 64,
    Beta     = 128,
    Rc       = 192,
    Official = 255
};

struct AutopilotCapabilitiesView {
    uint64_t mask{0};

    [[nodiscard]] constexpr bool supports_mission_int() const noexcept {
        return (mask & (1ULL << 2)) != 0;
    }
    [[nodiscard]] constexpr bool supports_param_union() const noexcept {
        return (mask & (1ULL << 4)) != 0;
    }
    [[nodiscard]] constexpr bool supports_ftp() const noexcept {
        return (mask & (1ULL << 5)) != 0;
    }
    [[nodiscard]] constexpr bool supports_mavlink2() const noexcept {
        return (mask & (1ULL << 12)) != 0;
    }
};

struct SemVerView {
    uint8_t major{0};
    uint8_t minor{0};
    uint8_t patch{0};
    FirmwareType type{FirmwareType::Dev};

    [[nodiscard]] static constexpr SemVerView from_raw(uint32_t raw) noexcept {
        return {
            .major = static_cast<uint8_t>((raw >> 24) & 0xFF),
            .minor = static_cast<uint8_t>((raw >> 16) & 0xFF),
            .patch = static_cast<uint8_t>((raw >> 8) & 0xFF),
            .type  = static_cast<FirmwareType>(raw & 0xFF)
        };
    }

    [[nodiscard]] std::string to_string() const {
        std::string_view suffix;
        switch (type) {
            case FirmwareType::Dev:      suffix = "-dev"; break;
            case FirmwareType::Alpha:    suffix = "-alpha"; break;
            case FirmwareType::Beta:     suffix = "-beta"; break;
            case FirmwareType::Rc:       suffix = "-rc"; break;
            case FirmwareType::Official: suffix = ""; break;
        }
        return std::format("v{}.{}.{}{}", major, minor, patch, suffix);
    }
};
