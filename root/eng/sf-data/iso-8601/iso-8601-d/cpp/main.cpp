#include <string_view>
#include <optional>
#include <chrono>
#include <cstdint>

struct ParsedTimestamp {
    std::chrono::sys_seconds utc_time{};
    int16_t offset_minutes{0};
    bool leap_second{false};
};

class Iso8601Parser {
    static constexpr int64_t civil_to_days(int32_t y, uint32_t m, uint32_t d) noexcept {
        y -= (m <= 2);
        const int32_t era = (y >= 0 ? y : y - 399) / 400;
        const uint32_t yoe = static_cast<uint32_t>(y - era * 400);
        const uint32_t doy = (153 * (m > 2 ? m - 3 : m + 9) + 2) / 5 + d - 1;
        const uint32_t doe = yoe * 365 + yoe / 4 - yoe / 100 + doy;
        return static_cast<int64_t>(era) * 146097 + static_cast<int64_t>(doe) - 719468;
    }

    static constexpr uint32_t p2(const char* s) noexcept {
        return static_cast<uint32_t>(s[0] * 10 + s[1] - 528);
    }
    static constexpr uint32_t p4(const char* s) noexcept {
        return static_cast<uint32_t>(s[0] * 1000 + s[1] * 100 + s[2] * 10 + s[3] - 53328);
    }

public:
    static constexpr std::optional<ParsedTimestamp> parse(std::string_view sv) noexcept {
        if (sv.size() < 20 || sv[4] != '-' || sv[7] != '-' ||
            (sv[10] != 'T' && sv[10] != ' ') || sv[13] != ':' || sv[16] != ':') {
            return std::nullopt;
        }

        const auto year = static_cast<int32_t>(p4(sv.data()));
        const auto mon  = p2(sv.data() + 5);
        const auto day  = p2(sv.data() + 8);
        const auto hour = p2(sv.data() + 11);
        const auto min  = p2(sv.data() + 14);
        const auto sec  = p2(sv.data() + 17);

        if (mon < 1 || mon > 12 || day < 1 || day > 31 || hour > 23 || min > 59 || sec > 60) {
            return std::nullopt;
        }

        const bool is_leap = (sec == 60);
        const uint32_t eff_sec = is_leap ? 59 : sec;

        int16_t offset_mins = 0;
        if (sv[19] == 'Z' || sv[19] == 'z') {
            offset_mins = 0;
        } else if ((sv[19] == '+' || sv[19] == '-') && sv.size() >= 25 && sv[22] == ':') {
            const auto oh = p2(sv.data() + 20);
            const auto om = p2(sv.data() + 23);
            if (oh > 23 || om > 59) return std::nullopt;
            offset_mins = static_cast<int16_t>(oh * 60 + om);
            if (sv[19] == '-') offset_mins = -offset_mins;
        } else {
            return std::nullopt;
        }

        const auto days = civil_to_days(year, mon, day);
        const auto local_secs = days * 86400 + hour * 3600 + min * 60 + eff_sec;
        const auto utc_secs = local_secs - offset_mins * 60;

        return ParsedTimestamp{
            std::chrono::sys_seconds{std::chrono::seconds{utc_secs}},
            offset_mins,
            is_leap
        };
    }
};
