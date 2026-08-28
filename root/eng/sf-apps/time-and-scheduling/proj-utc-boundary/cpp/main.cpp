// Межа: настінний час ↔ мить, ISO-8601 та високосні секунди на C++20.
#include <iostream>
#include <string>
#include <string_view>
#include <optional>
#include <chrono>
#include <charconv>
#include <algorithm>
#include <vector>
#include <array>

namespace time_boundary {

enum class ResolveKind { Exact, Gap, Ambiguous };

struct WallTime {
    int year{1970};
    int month{1};
    int day{1};
    int hour{0};
    int minute{0};
    int second{0};
    int ms{0};
    bool is_leap_second{false};
};

struct ResolvedTime {
    std::chrono::sys_time<std::chrono::milliseconds> instant;
    ResolveKind kind{ResolveKind::Exact};
};

struct Iso8601Result {
    WallTime wall;
    std::optional<std::chrono::minutes> offset;
    bool is_utc{false};
    bool valid{false};
};

constexpr bool is_leap_year(int y) noexcept {
    return (y % 4 == 0 && y % 100 != 0) || (y % 400 == 0);
}

constexpr int days_in_month(int y, int m) noexcept {
    constexpr std::array<int, 12> kDays{31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};
    if (m == 2 && is_leap_year(y)) return 29;
    return (m >= 1 && m <= 12) ? kDays[m - 1] : 0;
}

// Запит зсуву зони для конкретної точки на осі UTC
inline std::chrono::milliseconds zone_offset(std::chrono::sys_time<std::chrono::milliseconds> instant,
                                             std::string_view zone) {
    if (zone == "Europe/Kyiv") {
        using namespace std::chrono;
        auto march_trans = sys_days{2026y/March/29} + 1h;
        auto oct_trans   = sys_days{2026y/October/25} + 1h;
        if (instant >= march_trans && instant < oct_trans) {
            return hours{3};
        }
        return hours{2};
    }
    if (zone == "Asia/Tokyo") {
        return std::chrono::hours{9};
    }
    return std::chrono::milliseconds{0};
}

// Неблокуючий парсер ISO-8601 без динамічних алокацій
inline Iso8601Result parse_iso8601(std::string_view sv) noexcept {
    Iso8601Result res;
    if (sv.size() < 10) return res;

    auto parse_int = [](std::string_view s, int& out) noexcept -> bool {
        auto [ptr, ec] = std::from_chars(s.data(), s.data() + s.size(), out);
        return ec == std::errc{} && ptr == s.data() + s.size();
    };

    int y = 0, mo = 0, d = 0;
    if (!parse_int(sv.substr(0, 4), y) || sv[4] != '-' ||
        !parse_int(sv.substr(5, 2), mo) || sv[7] != '-' ||
        !parse_int(sv.substr(8, 2), d)) {
        return res;
    }

    if (mo < 1 || mo > 12 || d < 1 || d > days_in_month(y, mo)) return res;

    res.wall.year = y;
    res.wall.month = mo;
    res.wall.day = d;

    if (sv.size() == 10) {
        res.valid = true;
        return res;
    }

    if (sv[10] != 'T' && sv[10] != ' ') return res;
    std::string_view time_part = sv.substr(11);
    if (time_part.size() < 5) return res;

    int h = 0, mi = 0, s = 0;
    if (!parse_int(time_part.substr(0, 2), h) || time_part[2] != ':' ||
        !parse_int(time_part.substr(3, 2), mi)) {
        return res;
    }

    if (h < 0 || h > 23 || mi < 0 || mi > 59) return res;
    res.wall.hour = h;
    res.wall.minute = mi;

    size_t offset_pos = 5;
    if (time_part.size() >= 8 && time_part[5] == ':') {
        if (!parse_int(time_part.substr(6, 2), s)) return res;
        if (s < 0 || s > 60) return res;
        res.wall.second = (s == 60) ? 59 : s;
        res.wall.is_leap_second = (s == 60);
        offset_pos = 8;
    }

    if (offset_pos < time_part.size()) {
        std::string_view tz_sub = time_part.substr(offset_pos);
        if (tz_sub == "Z" || tz_sub == "z") {
            res.is_utc = true;
            res.offset = std::chrono::minutes{0};
        } else if (tz_sub.starts_with('+') || tz_sub.starts_with('-')) {
            int off_h = 0, off_m = 0;
            int sign = tz_sub[0] == '-' ? -1 : 1;
            if (tz_sub.size() >= 6 && tz_sub[3] == ':' &&
                parse_int(tz_sub.substr(1, 2), off_h) &&
                parse_int(tz_sub.substr(4, 2), off_m)) {
                res.offset = std::chrono::minutes{sign * (off_h * 60 + off_m)};
            }
        }
    }

    res.valid = true;
    return res;
}

// Настінний час + назва зони → мить і діагностика переходу
inline ResolvedTime resolve_local(const WallTime& w, std::string_view zone) {
    using namespace std::chrono;
    auto ymd = year{w.year} / month{static_cast<unsigned>(w.month)} / day{static_cast<unsigned>(w.day)};
    sys_days sd{ymd};
    auto as_if_utc = sd + hours{w.hour} + minutes{w.minute} + seconds{w.second} + milliseconds{w.ms};

    auto before = zone_offset(as_if_utc - 24h, zone);
    auto after  = zone_offset(as_if_utc + 24h, zone);

    std::vector<sys_time<milliseconds>> valid;
    auto test_candidate = [&](milliseconds off) {
        auto cand = as_if_utc - off;
        if (zone_offset(cand, zone) == off) {
            valid.push_back(cand);
        }
    };

    test_candidate(before);
    if (before != after) test_candidate(after);

    if (valid.size() == 1) {
        return ResolvedTime{.instant = valid[0], .kind = ResolveKind::Exact};
    }
    if (valid.size() == 2) {
        return ResolvedTime{.instant = std::min(valid[0], valid[1]), .kind = ResolveKind::Ambiguous};
    }
    return ResolvedTime{.instant = as_if_utc - std::min(before, after), .kind = ResolveKind::Gap};
}

// Форматування миті в настінний напис читача
inline std::string format_in_zone(std::chrono::sys_time<std::chrono::milliseconds> instant,
                                  std::string_view zone) {
    using namespace std::chrono;
    auto off = zone_offset(instant, zone);
    auto local_time = instant + off;
    auto dp = floor<days>(local_time);
    year_month_day ymd{dp};
    auto tod = make_time(local_time - dp);

    int off_min = static_cast<int>(duration_cast<minutes>(off).count());
    char sign = off_min >= 0 ? '+' : '-';
    if (off_min < 0) off_min = -off_min;

    auto pad2 = [](int v) -> std::string {
        return v < 10 ? "0" + std::to_string(v) : std::to_string(v);
    };

    std::string out;
    out.reserve(32);
    out += std::to_string(static_cast<int>(ymd.year())) + "-";
    out += pad2(static_cast<unsigned>(ymd.month())) + "-";
    out += pad2(static_cast<unsigned>(ymd.day())) + " ";
    out += pad2(static_cast<int>(tod.hours().count())) + ":";
    out += pad2(static_cast<int>(tod.minutes().count())) + ":";
    out += pad2(static_cast<int>(tod.seconds().count())) + " ";
    out += sign;
    out += pad2(off_min / 60) + ":";
    out += pad2(off_min % 60);
    return out;
}

// Обчислення меж календарної доби користувача на осі митей
inline std::pair<std::chrono::sys_time<std::chrono::milliseconds>,
                 std::chrono::sys_time<std::chrono::milliseconds>>
day_bounds(std::chrono::year_month_day day, std::string_view zone) {
    using namespace std::chrono;
    WallTime start_w{static_cast<int>(day.year()), static_cast<int>(static_cast<unsigned>(day.month())),
                     static_cast<int>(static_cast<unsigned>(day.day())), 0, 0, 0, 0, false};
    
    sys_days next_sd = sys_days{day} + days{1};
    year_month_day next_day{next_sd};
    WallTime end_w{static_cast<int>(next_day.year()), static_cast<int>(static_cast<unsigned>(next_day.month())),
                   static_cast<int>(static_cast<unsigned>(next_day.day())), 0, 0, 0, 0, false};

    return {resolve_local(start_w, zone).instant, resolve_local(end_w, zone).instant};
}

} // namespace time_boundary
