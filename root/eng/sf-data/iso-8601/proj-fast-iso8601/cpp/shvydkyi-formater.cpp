#include <string_view>
#include <array>
#include <chrono>
#include <cstdint>

class FastIso8601Formatter {
    static constexpr std::array<char, 200> DIGITS_LUT = {
        '0','0','0','1','0','2','0','3','0','4','0','5','0','6','0','7','0','8','0','9',
        '1','0','1','1','1','2','1','3','1','4','1','5','1','6','1','7','1','8','1','9',
        '2','0','2','1','2','2','2','3','2','4','2','5','2','6','2','7','2','8','2','9',
        '3','0','3','1','3','2','3','3','3','4','3','5','3','6','3','7','3','8','3','9',
        '4','0','4','1','4','2','4','3','4','4','4','5','4','6','4','7','4','8','4','9',
        '5','0','5','1','5','2','5','3','5','4','5','5','5','6','5','7','5','8','5','9',
        '6','0','6','1','6','2','6','3','6','4','6','5','6','6','6','7','6','8','6','9',
        '7','0','7','1','7','2','7','3','7','4','7','5','7','6','7','7','7','8','7','9',
        '8','0','8','1','8','2','8','3','8','4','8','5','8','6','8','7','8','8','8','9',
        '9','0','9','1','9','2','9','3','9','4','9','5','9','6','9','7','9','8','9','9'
    };

    static constexpr void write2(char* dest, uint32_t val) noexcept {
        const uint32_t idx = val * 2;
        dest[0] = DIGITS_LUT[idx];
        dest[1] = DIGITS_LUT[idx + 1];
    }

public:
    static constexpr std::array<char, 21> format_utc(std::chrono::sys_seconds tp) noexcept {
        std::array<char, 21> buf{};
        int64_t unix_secs = tp.time_since_epoch().count();

        int64_t days = unix_secs / 86400;
        int32_t rem  = static_cast<int32_t>(unix_secs % 86400);
        if (rem < 0) {
            rem += 86400;
            days -= 1;
        }

        const auto hour = static_cast<uint32_t>(rem / 3600);
        rem %= 3600;
        const auto min  = static_cast<uint32_t>(rem / 60);
        const auto sec  = static_cast<uint32_t>(rem % 60);

        days += 719468;
        const int64_t era = (days >= 0 ? days : days - 146096) / 146097;
        const auto doe = static_cast<uint32_t>(days - era * 146097);
        const auto yoe = (doe - doe / 1460 + doe / 36524 - doe / 146096) / 365;
        auto y = static_cast<int32_t>(yoe) + static_cast<int32_t>(era) * 400;
        const auto doy = doe - (365 * yoe + yoe / 4 - yoe / 100);
        const auto mp = (5 * doy + 2) / 153;
        const auto d = doy - (153 * mp + 2) / 5 + 1;
        const auto m = mp < 10 ? mp + 3 : mp - 9;
        if (m <= 2) y += 1;

        write2(buf.data(), static_cast<uint32_t>(y / 100));
        write2(buf.data() + 2, static_cast<uint32_t>(y % 100));
        buf[4] = '-';
        write2(buf.data() + 5, m);
        buf[7] = '-';
        write2(buf.data() + 8, d);
        buf[10] = 'T';
        write2(buf.data() + 11, hour);
        buf[13] = ':';
        write2(buf.data() + 14, min);
        buf[16] = ':';
        write2(buf.data() + 17, sec);
        buf[19] = 'Z';
        buf[20] = '\0';

        return buf;
    }
};
