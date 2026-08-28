// ============================================================================
// zero_alloc_engine.hpp (C++20)
// Ідіоматична C++20 версія рушія рекурентності з нульовим виділенням купи.
// ============================================================================
#include <chrono>
#include <bitset>
#include <string_view>
#include <optional>
#include <cstdint>
#include <bit>
#include <array>

namespace zero_alloc {

enum class Freq : uint8_t {
    None, Secondly, Minutely, Hourly, Daily, Weekly, Monthly, Yearly
};

struct WeekdayNum {
    int8_t ord{0}; // -5..+5
    int8_t day{0}; // 0 = SU, 1 = MO...
};

struct RRule {
    Freq freq{Freq::None};
    uint32_t interval{1};
    uint32_t count{0};
    int64_t until_utc{0};
    uint16_t by_month_mask{0};
    uint32_t by_monthday_mask{0};
    uint32_t by_neg_monthday{0};
    std::array<WeekdayNum, 8> by_day{};
    uint8_t by_day_count{0};
    std::array<int8_t, 8> by_setpos{};
    uint8_t by_setpos_count{0};
    uint8_t wkst{1};
    bool has_count{false};
    bool has_until{false};
};

struct Cron {
    std::bitset<60> sec_mask{1}; // Секунда 0
    std::bitset<60> min_mask{};
    std::bitset<24> hour_mask{};
    std::bitset<32> dom_mask{};
    std::bitset<13> mon_mask{};
    std::bitset<7>  dow_mask{};
    bool dom_is_star{true};
    bool dow_is_star{true};
};

class Parser {
public:
    static constexpr std::optional<uint32_t> parse_uint(std::string_view& sv) noexcept {
        if (sv.empty() || sv.front() < '0' || sv.front() > '9') return std::nullopt;
        uint32_t val = 0;
        size_t idx = 0;
        while (idx < sv.size() && sv[idx] >= '0' && sv[idx] <= '9') {
            val = val * 10 + static_cast<uint32_t>(sv[idx] - '0');
            idx++;
        }
        sv.remove_prefix(idx);
        return val;
    }

    static std::optional<Cron> parse_cron(std::string_view sv) noexcept {
        Cron cron{};
        cron.sec_mask = 1;

        auto parse_field = [](std::string_view& s, int min_val, int max_val, auto& mask, bool& is_star) -> bool {
            mask.reset();
            is_star = false;
            if (s.empty()) return false;

            if (s.front() == '*') {
                is_star = true;
                s.remove_prefix(1);
                if (!s.empty() && s.front() == '/') {
                    s.remove_prefix(1);
                    auto step_opt = parse_uint(s);
                    if (!step_opt || *step_opt == 0) return false;
                    for (int i = min_val; i <= max_val; i += static_cast<int>(*step_opt)) {
                        mask.set(i);
                    }
                    is_star = false;
                } else {
                    for (int i = min_val; i <= max_val; ++i) mask.set(i);
                }
                return true;
            }

            while (!s.empty() && s.front() != ' ' && s.front() != '\t') {
                auto start_opt = parse_uint(s);
                if (!start_opt || *start_opt < static_cast<uint32_t>(min_val) || *start_opt > static_cast<uint32_t>(max_val)) return false;

                uint32_t stop = *start_opt;
                uint32_t step = 1;

                if (!s.empty() && s.front() == '-') {
                    s.remove_prefix(1);
                    auto stop_opt = parse_uint(s);
                    if (!stop_opt || *stop_opt < *start_opt || *stop_opt > static_cast<uint32_t>(max_val)) return false;
                    stop = *stop_opt;
                }

                if (!s.empty() && s.front() == '/') {
                    s.remove_prefix(1);
                    auto step_opt = parse_uint(s);
                    if (!step_opt || *step_opt == 0) return false;
                    step = *step_opt;
                }

                for (uint32_t i = *start_opt; i <= stop; i += step) {
                    mask.set(i);
                }

                if (!s.empty() && s.front() == ',') {
                    s.remove_prefix(1);
                } else {
                    break;
                }
            }
            return true;
        };

        auto skip_spaces = [](std::string_view& s) {
            while (!s.empty() && (s.front() == ' ' || s.front() == '\t')) s.remove_prefix(1);
        };

        skip_spaces(sv);
        bool dummy = false;
        if (!parse_field(sv, 0, 59, cron.min_mask, dummy)) return std::nullopt;
        skip_spaces(sv);
        if (!parse_field(sv, 0, 23, cron.hour_mask, dummy)) return std::nullopt;
        skip_spaces(sv);
        if (!parse_field(sv, 1, 31, cron.dom_mask, cron.dom_is_star)) return std::nullopt;
        skip_spaces(sv);
        if (!parse_field(sv, 1, 12, cron.mon_mask, dummy)) return std::nullopt;
        skip_spaces(sv);
        
        std::bitset<8> raw_dow{};
        if (!parse_field(sv, 0, 7, raw_dow, cron.dow_is_star)) return std::nullopt;
        if (raw_dow.test(7)) {
            raw_dow.set(0);
            raw_dow.reset(7);
        }
        for (size_t i = 0; i < 7; ++i) {
            if (raw_dow.test(i)) cron.dow_mask.set(i);
        }

        return cron;
    }
};

class Engine {
public:
    [[nodiscard]] static std::optional<std::chrono::sys_seconds> next_cron_time(
        const Cron& cron,
        std::chrono::sys_seconds from_utc,
        const std::chrono::time_zone* tz) noexcept
    {
        using namespace std::chrono;

        auto local_tp = tz->to_local(from_utc);
        auto local_days_tp = floor<days>(local_tp);
        year_month_day ymd{local_days_tp};
        hh_mm_ss hms{floor<seconds>(local_tp - local_days_tp)};

        int y = static_cast<int>(ymd.year());
        int m = static_cast<unsigned>(ymd.month());
        int d = static_cast<unsigned>(ymd.day());
        int hour = static_cast<int>(hms.hours().count());
        int min = static_cast<int>(hms.minutes().count());
        int sec = static_cast<int>(hms.seconds().count()) + 1;

        int iterations = 0;
        while (iterations++ < 5000) {
            if (!cron.mon_mask.test(m)) {
                uint64_t raw = cron.mon_mask.to_ullong() & ~((1ULL << m) - 1);
                if (raw == 0) {
                    y++;
                    m = std::countr_zero(cron.mon_mask.to_ullong());
                } else {
                    m = std::countr_zero(raw);
                }
                d = 1; hour = 0; min = 0; sec = 0;
                continue;
            }

            year_month_day cur_ymd{year{y}, month{static_cast<unsigned>(m)}, day{static_cast<unsigned>(d)}};
            if (!cur_ymd.ok()) {
                m++;
                if (m > 12) { m = 1; y++; }
                d = 1; hour = 0; min = 0; sec = 0;
                continue;
            }

            weekday wd{sys_days{cur_ymd}};
            unsigned dow = wd.c_encoding();

            bool dom_match = cron.dom_mask.test(d);
            bool dow_match = cron.dow_mask.test(dow);
            bool day_valid = (!cron.dom_is_star && !cron.dow_is_star)
                ? (dom_match || dow_match)
                : (!cron.dom_is_star ? dom_match : (!cron.dow_is_star ? dow_match : true));

            if (!day_valid) {
                d++;
                hour = 0; min = 0; sec = 0;
                continue;
            }

            if (!cron.hour_mask.test(hour)) {
                uint64_t raw = cron.hour_mask.to_ullong() & ~((1ULL << hour) - 1);
                if (raw == 0) {
                    d++;
                    hour = std::countr_zero(cron.hour_mask.to_ullong());
                } else {
                    hour = std::countr_zero(raw);
                }
                min = 0; sec = 0;
                continue;
            }

            if (!cron.min_mask.test(min)) {
                uint64_t raw = cron.min_mask.to_ullong() & ~((1ULL << min) - 1);
                if (raw == 0) {
                    hour++;
                    min = std::countr_zero(cron.min_mask.to_ullong());
                    if (hour > 23) { hour = 0; d++; }
                } else {
                    min = std::countr_zero(raw);
                }
                sec = 0;
                continue;
            }

            if (!cron.sec_mask.test(sec)) {
                uint64_t raw = cron.sec_mask.to_ullong() & ~((1ULL << sec) - 1);
                if (raw == 0) {
                    min++;
                    sec = std::countr_zero(cron.sec_mask.to_ullong());
                    if (min > 59) {
                        min = 0; hour++;
                        if (hour > 23) { hour = 0; d++; }
                    }
                } else {
                    sec = std::countr_zero(raw);
                }
                continue;
            }

            local_seconds target_local{
                sys_days{year{y}/month{static_cast<unsigned>(m)}/day{static_cast<unsigned>(d)}} +
                hours{hour} + minutes{min} + seconds{sec}
            };

            try {
                auto info = tz->get_info(target_local);
                if (info.result == local_info::nonexistent) {
                    return info.second.begin;
                }
                return tz->to_sys(target_local, choose::earliest);
            } catch (...) {
                return std::nullopt;
            }
        }
        return std::nullopt;
    }
};

} // namespace zero_alloc
