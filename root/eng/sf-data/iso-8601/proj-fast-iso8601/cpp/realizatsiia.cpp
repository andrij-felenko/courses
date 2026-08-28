#include <string_view>
#include <optional>
#include <chrono>
#include <cstdint>

struct IsoDateTime {
    std::chrono::sys_seconds time_point{};
    std::chrono::nanoseconds subseconds{};
    int16_t offset_minutes{0};
    bool leap_second{false};
};

class FastIso8601 {
    static constexpr int64_t days_from_civil(int32_t y, uint32_t m, uint32_t d) noexcept {
        y -= (m <= 2);
        const int32_t era = (y >= 0 ? y : y - 399) / 400;
        const uint32_t yoe = static_cast<uint32_t>(y - era * 400);
        const uint32_t doy = (153 * (m > 2 ? m - 3 : m + 9) + 2) / 5 + d - 1;
        const uint32_t doe = yoe * 365 + yoe / 4 - yoe / 100 + doy;
        return static_cast<int64_t>(era) * 146097 + static_cast<int64_t>(doe) - 719468;
    }

    static constexpr bool is_valid_date(int32_t y, uint32_t m, uint32_t d) noexcept {
        if (m < 1 || m > 12 || d < 1 || d > 31) return false;
        if (m == 2) {
            const bool leap = (y % 4 == 0 && (y % 100 != 0 || y % 400 == 0));
            return d <= (leap ? 29u : 28u);
        }
        if (m == 4 || m == 6 || m == 9 || m == 11) return d <= 30u;
        return true;
    }

    static constexpr uint32_t parse2(const char* s) noexcept {
        return static_cast<uint32_t>(s[0] * 10 + s[1] - 528);
    }

    static constexpr uint32_t parse4(const char* s) noexcept {
        return static_cast<uint32_t>(s[0] * 1000 + s[1] * 100 + s[2] * 10 + s[3] - 53328);
    }

public:
    static constexpr std::optional<IsoDateTime> parse(std::string_view sv) noexcept {
        if (sv.size() < 20) return std::nullopt;

        if (sv[4] != '-' || sv[7] != '-' || (sv[10] != 'T' && sv[10] != ' ') ||
            sv[13] != ':' || sv[16] != ':') {
            return std::nullopt;
        }

        const auto year  = static_cast<int32_t>(parse4(sv.data()));
        const auto month = parse2(sv.data() + 5);
        const auto day   = parse2(sv.data() + 8);
        const auto hour  = parse2(sv.data() + 11);
        const auto min   = parse2(sv.data() + 14);
        const auto sec   = parse2(sv.data() + 17);

        if (!is_valid_date(year, month, day) || hour > 23 || min > 59 || sec > 60) {
            return std::nullopt;
        }

        const bool is_leap = (sec == 60);
        const uint32_t eff_sec = is_leap ? 59 : sec;

        size_t idx = 19;
        int32_t nanos = 0;

        if (idx < sv.size() && (sv[idx] == '.' || sv[idx] == ',')) {
            idx++;
            int32_t mult = 100'000'000;
            while (idx < sv.size() && sv[idx] >= '0' && sv[idx] <= '9') {
                if (mult > 0) {
                    nanos += (sv[idx] - '0') * mult;
                    mult /= 10;
                }
                idx++;
            }
        }

        int16_t offset_mins = 0;
        if (idx < sv.size()) {
            if (sv[idx] == 'Z' || sv[idx] == 'z') {
                offset_mins = 0;
            } else if ((sv[idx] == '+' || sv[idx] == '-') && (sv.size() - idx >= 6)) {
                if (sv[idx + 3] != ':') return std::nullopt;
                const auto off_h = parse2(sv.data() + idx + 1);
                const auto off_m = parse2(sv.data() + idx + 4);
                if (off_h > 23 || off_m > 59) return std::nullopt;
                offset_mins = static_cast<int16_t>(off_h * 60 + off_m);
                if (sv[idx] == '-') offset_mins = -offset_mins;
            } else {
                return std::nullopt;
            }
        }

        const auto days = days_from_civil(year, month, day);
        const auto local_secs = days * 86400 + hour * 3600 + min * 60 + eff_sec;
        const auto utc_secs = local_secs - offset_mins * 60;

        return IsoDateTime{
            std::chrono::sys_seconds{std::chrono::seconds{utc_secs}},
            std::chrono::nanoseconds{nanos},
            offset_mins,
            is_leap
        };
    }
};
