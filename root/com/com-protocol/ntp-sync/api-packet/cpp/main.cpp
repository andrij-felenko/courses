#include <cstdint>
#include <string_view>
#include <array>
#include <cstring>
#include <bit>

#pragma pack(push, 1)

struct NtpTimestamp {
    uint32_t seconds{0};
    uint32_t fraction{0};

    static constexpr uint32_t UnixEpochOffset = 2208988800ULL;
    static constexpr double FractionScale = 4294967296.0;

    [[nodiscard]] constexpr double to_unix_seconds() const noexcept {
        const uint32_t s = std::byteswap(seconds);
        const uint32_t f = std::byteswap(fraction);
        if (s == 0 && f == 0) return 0.0;
        return static_cast<double>(s - UnixEpochOffset) + (static_cast<double>(f) / FractionScale);
    }

    static constexpr NtpTimestamp from_unix_seconds(double t) noexcept {
        const auto s = static_cast<uint32_t>(t + static_cast<double>(UnixEpochOffset));
        const double frac_part = t - static_cast<double>(static_cast<uint32_t>(t));
        const auto f = static_cast<uint32_t>(frac_part * FractionScale);
        return {std::byteswap(s), std::byteswap(f)};
    }
};

struct NtpHeader {
    uint8_t      li_vn_mode{0};
    uint8_t      stratum{0};
    int8_t       poll{0};
    int8_t       precision{0};
    uint32_t     root_delay{0};
    uint32_t     root_dispersion{0};
    uint32_t     ref_id{0};
    NtpTimestamp ref_time{};
    NtpTimestamp origin_time{};
    NtpTimestamp rx_time{};
    NtpTimestamp tx_time{};

    [[nodiscard]] constexpr uint8_t leap_indicator() const noexcept {
        return (li_vn_mode >> 6) & 0x03;
    }

    [[nodiscard]] constexpr uint8_t version() const noexcept {
        return (li_vn_mode >> 3) & 0x07;
    }

    [[nodiscard]] constexpr uint8_t mode() const noexcept {
        return li_vn_mode & 0x07;
    }

    constexpr void set_control(uint8_t li, uint8_t vn, uint8_t mode) noexcept {
        li_vn_mode = static_cast<uint8_t>(((li & 0x03) << 6) | ((vn & 0x07) << 3) | (mode & 0x07));
    }

    [[nodiscard]] bool is_kiss_of_death(std::array<char, 5>& out_code) const noexcept {
        if (stratum == 0) {
            std::memcpy(out_code.data(), &ref_id, 4);
            out_code[4] = '\0';
            return true;
        }
        return false;
    }
};

#pragma pack(pop)
static_assert(sizeof(NtpHeader) == 48, "NTP header must be strictly 48 bytes");
