// ============================================================================
// recurrence_engine.hpp (C++20)
// Ідіоматичний рушій на std::chrono, std::bitset та константних виразах.
// ============================================================================
#include <chrono>
#include <bitset>
#include <optional>
#include <string_view>
#include <cstdint>
#include <bit>

namespace scheduling {

struct CronSchedule {
    std::bitset<60> sec_mask;
    std::bitset<60> min_mask;
    std::bitset<24> hour_mask;
    std::bitset<32> dom_mask; // Біти 1..31
    std::bitset<13> mon_mask; // Біти 1..12
    std::bitset<7>  dow_mask; // Біти 0..6 (0 = Неділя)
    bool dom_is_star{true};
    bool dow_is_star{true};
};

class RecurrenceEngine {
public:
    [[nodiscard]] static constexpr bool is_leap_year(std::chrono::year y) noexcept {
        return y.is_leap();
    }

    [[nodiscard]] static std::optional<std::chrono::sys_seconds> next_cron_occurrence(
        const CronSchedule& cron,
        std::chrono::sys_seconds from_utc,
        const std::chrono::time_zone* tz)
    {
        using namespace std::chrono;

        // Переводимо UTC у локальний цивільний час поясу
        auto local_tp = tz->to_local(from_utc);
        auto local_days_tp = floor<days>(local_tp);
        year_month_day ymd{local_days_tp};
        hh_mm_ss hms{floor<seconds>(local_tp - local_days_tp)};

        int y = static_cast<int>(ymd.year());
        int m = static_cast<unsigned>(ymd.month());
        int d = static_cast<unsigned>(ymd.day());
        int hour = hms.hours().count();
        int min = hms.minutes().count();
        int sec = hms.seconds().count() + 1; // Шукаємо строго після заданого моменту

        int iterations = 0;
        while (iterations++ < 5000) {
            // 1. Місяць
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

            // 2. День місяця та день тижня
            year_month_day current_ymd{year{y}, month{static_cast<unsigned>(m)}, day{static_cast<unsigned>(d)}};
            if (!current_ymd.ok()) {
                m++;
                if (m > 12) { m = 1; y++; }
                d = 1; hour = 0; min = 0; sec = 0;
                continue;
            }

            weekday wd{sys_days{current_ymd}};
            unsigned dow = wd.c_encoding(); // 0 = Неділя, 1 = Понеділок...

            bool dom_match = cron.dom_mask.test(d);
            bool dow_match = cron.dow_mask.test(dow);
            bool day_valid = false;

            if (!cron.dom_is_star && !cron.dow_is_star) {
                day_valid = dom_match || dow_match; // POSIX OR
            } else if (!cron.dom_is_star) {
                day_valid = dom_match;
            } else if (!cron.dow_is_star) {
                day_valid = dow_match;
            } else {
                day_valid = true;
            }

            if (!day_valid) {
                d++;
                hour = 0; min = 0; sec = 0;
                continue;
            }

            // 3. Година
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

            // 4. Хвилина
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

            // 5. Секунда
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

            // Складання локального часу та переведення в UTC з урахуванням DST
            local_seconds target_local{
                sys_days{year{y}/month{static_cast<unsigned>(m)}/day{static_cast<unsigned>(d)}} +
                hours{hour} + minutes{min} + seconds{sec}
            };

            try {
                // choose::earliest розв'язує накладання на користь першої появи (fold=0)
                auto info = tz->get_info(target_local);
                if (info.result == local_info::nonexistent) {
                    // Стратегія Gap: зміщення до першого валідного моменту після розриву
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

} // namespace scheduling
