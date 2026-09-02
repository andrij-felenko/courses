#include "schedule.hpp"

#include <algorithm>
#include <array>
#include <cctype>
#include <cerrno>
#include <charconv>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <format>
#include <iostream>

#include <sys/inotify.h>
#include <unistd.h>

namespace minicron {
namespace {

using namespace std::string_view_literals;
namespace fs = std::filesystem;

constexpr std::array kMonthNames = {
    "jan"sv, "feb"sv, "mar"sv, "apr"sv, "may"sv, "jun"sv,
    "jul"sv, "aug"sv, "sep"sv, "oct"sv, "nov"sv, "dec"sv
};
constexpr std::array kDowNames = {
    "sun"sv, "mon"sv, "tue"sv, "wed"sv, "thu"sv, "fri"sv, "sat"sv
};

struct FieldDef {
    std::string_view name;
    int lo;
    int hi;
    std::span<const std::string_view> names;
    int names_base;      // число, якому відповідає names[0]
    bool wrap_seven;     // день тижня: 7 і 0 — та сама неділя
};

const std::array<FieldDef, 5> kFields = {
    FieldDef{"minute"sv,       0, 59, {}, 0, false},
    FieldDef{"hour"sv,         0, 23, {}, 0, false},
    FieldDef{"day of month"sv, 1, 31, {}, 0, false},
    FieldDef{"month"sv,        1, 12, kMonthNames, 1, false},
    FieldDef{"day of week"sv,  0,  7, kDowNames, 0, true},
};

// Мнемонічні макроси демон замінює на звичайні п'ять полів під час розбору.
constexpr std::array<std::pair<std::string_view, std::string_view>, 7> kMacros = {{
    {"@yearly"sv,   "0 0 1 1 *"sv},
    {"@annually"sv, "0 0 1 1 *"sv},
    {"@monthly"sv,  "0 0 1 * *"sv},
    {"@weekly"sv,   "0 0 * * 0"sv},
    {"@daily"sv,    "0 0 * * *"sv},
    {"@midnight"sv, "0 0 * * *"sv},
    {"@hourly"sv,   "0 * * * *"sv},
}};

bool iequal(std::string_view a, std::string_view b)
{
    return std::ranges::equal(a, b, [](char x, char y) {
        return std::tolower(static_cast<unsigned char>(x)) ==
               std::tolower(static_cast<unsigned char>(y));
    });
}

std::string_view ltrim(std::string_view s)
{
    const auto pos = s.find_first_not_of(" \t"sv);
    return (pos == std::string_view::npos) ? std::string_view{} : s.substr(pos);
}

std::optional<int> to_number(std::string_view s)
{
    int value = 0;
    const auto* first = s.data();
    const auto* last = s.data() + s.size();
    const auto [ptr, ec] = std::from_chars(first, last, value);
    if (ec != std::errc{} || ptr != last) {
        return std::nullopt;
    }
    return value;
}

struct Value {
    int number = 0;
    bool named = false;
};

std::expected<Value, std::string> parse_value(std::string_view text, const FieldDef& def)
{
    Value value;
    if (const auto number = to_number(text); number.has_value()) {
        value = Value{*number, false};
    } else {
        // Назви місяців і днів тижня розпізнаються без урахування регістру.
        const auto found = std::ranges::find_if(def.names, [&](std::string_view name) {
            return text.size() == 3 && iequal(text, name);
        });
        if (found == def.names.end()) {
            return std::unexpected(std::format("нерозпізнане значення «{}»", text));
        }
        value = Value{def.names_base + static_cast<int>(found - def.names.begin()), true};
    }
    if (value.number < def.lo || value.number > def.hi) {
        return std::unexpected(std::format("значення {} поза діапазоном {}..{}",
                                           value.number, def.lo, def.hi));
    }
    return value;
}

// Одне поле: список елементів через кому, кожен — «*», значення, діапазон
// «a-b», з необов'язковим кроком «/n».
template <std::size_t N>
std::expected<std::bitset<N>, std::string> parse_field(std::string_view field,
                                                       const FieldDef& def)
{
    std::bitset<N> mask;
    if (field.empty()) {
        return std::unexpected(std::string{"порожнє поле"});
    }

    while (!field.empty()) {
        const auto comma = field.find(',');
        const std::string_view item = field.substr(0, comma);
        field = (comma == std::string_view::npos) ? std::string_view{}
                                                  : field.substr(comma + 1);
        if (item.empty()) {
            return std::unexpected(std::string{"порожній елемент списку"});
        }

        int step = 1;
        std::string_view range = item;
        const auto slash = item.find('/');
        if (slash != std::string_view::npos) {
            const auto parsed = to_number(item.substr(slash + 1));
            if (!parsed.has_value() || *parsed <= 0) {
                return std::unexpected(std::format("хибний крок у «{}»", item));
            }
            step = *parsed;
            range = item.substr(0, slash);
        }

        int lo = def.lo;
        int hi = def.hi;
        bool named = false;
        if (range != "*"sv) {
            if (const auto dash = range.find('-'); dash != std::string_view::npos) {
                const auto low = parse_value(range.substr(0, dash), def);
                if (!low) {
                    return std::unexpected(low.error());
                }
                const auto high = parse_value(range.substr(dash + 1), def);
                if (!high) {
                    return std::unexpected(high.error());
                }
                // Vixie забороняє змішувати число й назву в одному діапазоні.
                if (low->named != high->named) {
                    return std::unexpected(
                        std::format("у діапазоні «{}» змішано число й назву", range));
                }
                if (low->number > high->number) {
                    return std::unexpected(std::format("порожній діапазон «{}»", range));
                }
                lo = low->number;
                hi = high->number;
                named = low->named;
            } else {
                const auto single = parse_value(range, def);
                if (!single) {
                    return std::unexpected(single.error());
                }
                lo = single->number;
                // «5/10» читаємо як «5-max/10» — розширення cronie.
                hi = (slash != std::string_view::npos) ? def.hi : single->number;
                named = single->named;
            }
        }

        // Крок до символьних назв не застосовується (класичний Vixie).
        if (slash != std::string_view::npos && named) {
            return std::unexpected(
                std::string{"крок «/» не застосовується до назв — вживайте числа"});
        }

        for (int v = lo; v <= hi; v += step) {
            const auto bit = static_cast<std::size_t>((def.wrap_seven && v == 7) ? 0 : v);
            if (bit < N) {
                mask.set(bit);
            }
        }
    }
    return mask;
}

}  // namespace

std::string ParseError::message() const
{
    return std::format("bad {}: {}", field, detail);
}

std::expected<Schedule::Parsed, ParseError> Schedule::parse(std::string_view line)
{
    line = ltrim(line);

    if (line.starts_with('@')) {
        const auto end = line.find_first_of(" \t"sv);
        const std::string_view token = line.substr(0, end);
        const std::string_view rest =
            (end == std::string_view::npos) ? std::string_view{} : line.substr(end);

        if (iequal(token, "@reboot"sv)) {
            Schedule schedule;
            schedule.reboot_ = true;
            return Parsed{schedule, rest};
        }
        for (const auto& [name, spec] : kMacros) {
            if (iequal(token, name)) {
                auto expanded = parse(spec);
                if (!expanded) {
                    return std::unexpected(expanded.error());
                }
                return Parsed{expanded->schedule, rest};
            }
        }
        return std::unexpected(
            ParseError{"macro", std::format("невідомий макрос «{}»", token)});
    }

    std::array<std::string_view, 5> tokens{};
    std::string_view rest = line;
    for (std::size_t i = 0; i < tokens.size(); ++i) {
        rest = ltrim(rest);
        const auto end = rest.find_first_of(" \t"sv);
        tokens[i] = rest.substr(0, end);
        if (tokens[i].empty()) {
            return std::unexpected(
                ParseError{std::string{kFields[i].name}, "бракує поля розкладу"});
        }
        rest = (end == std::string_view::npos) ? std::string_view{} : rest.substr(end);
    }

    Schedule out;
    const auto minutes = parse_field<60>(tokens[0], kFields[0]);
    if (!minutes) {
        return std::unexpected(ParseError{std::string{kFields[0].name}, minutes.error()});
    }
    const auto hours = parse_field<24>(tokens[1], kFields[1]);
    if (!hours) {
        return std::unexpected(ParseError{std::string{kFields[1].name}, hours.error()});
    }
    const auto dom = parse_field<32>(tokens[2], kFields[2]);
    if (!dom) {
        return std::unexpected(ParseError{std::string{kFields[2].name}, dom.error()});
    }
    const auto months = parse_field<13>(tokens[3], kFields[3]);
    if (!months) {
        return std::unexpected(ParseError{std::string{kFields[3].name}, months.error()});
    }
    const auto dow = parse_field<7>(tokens[4], kFields[4]);
    if (!dow) {
        return std::unexpected(ParseError{std::string{kFields[4].name}, dow.error()});
    }

    out.minutes_ = *minutes;
    out.hours_ = *hours;
    out.months_ = *months;
    out.days_.dom = *dom;
    out.days_.dow = *dow;
    out.days_.dom_star = tokens[2].starts_with('*');
    out.days_.dow_star = tokens[4].starts_with('*');
    return Parsed{out, rest};
}

bool Schedule::matches(const std::tm& now) const noexcept
{
    if (reboot_) {
        return false;   // @reboot не має календарного збігу взагалі
    }
    if (now.tm_min < 0 || now.tm_min > 59 || now.tm_hour < 0 || now.tm_hour > 23 ||
        now.tm_mon < 0 || now.tm_mon > 11) {
        return false;
    }
    if (!minutes_.test(static_cast<std::size_t>(now.tm_min))) {
        return false;
    }
    if (!hours_.test(static_cast<std::size_t>(now.tm_hour))) {
        return false;
    }
    if (!months_.test(static_cast<std::size_t>(now.tm_mon + 1))) {
        return false;
    }
    return days_.matches(now);
}

std::chrono::seconds seconds_to_next_minute(std::chrono::system_clock::time_point now)
{
    using namespace std::chrono;
    const auto whole = time_point_cast<seconds>(now).time_since_epoch();
    return 60s - (whole % 60s);
}

SourceWatch::SourceWatch(std::span<const fs::path> paths)
    : paths_(paths.begin(), paths.end())
{
    // IN_CLOEXEC — щоб дескриптор не протік у завдання через exec;
    // IN_NONBLOCK — щоб читання порожньої черги не спинило демона.
    inotify_.reset(::inotify_init1(IN_CLOEXEC | IN_NONBLOCK));
    if (inotify_.valid()) {
        constexpr std::uint32_t mask =
            IN_MODIFY | IN_CREATE | IN_DELETE | IN_ATTRIB | IN_MOVED_TO |
            IN_MOVED_FROM | IN_CLOSE_WRITE | IN_DELETE_SELF | IN_MOVE_SELF;
        for (const auto& path : paths_) {
            if (::inotify_add_watch(inotify_.get(), path.c_str(), mask) < 0) {
                // Шляху ще може не бути — відступаємо на опитування: воно
                // переживає і зникнення, і появу файлу.
                std::cerr << std::format("minicron: inotify {}: {} — переходжу на stat()\n",
                                         path.string(), std::strerror(errno));
                inotify_.reset();
                break;
            }
        }
    }

    stamps_.resize(paths_.size());
    (void)stamps_changed();   // початковий знімок міток часу
}

bool SourceWatch::stamps_changed()
{
    bool changed = false;
    for (std::size_t i = 0; i < paths_.size(); ++i) {
        std::error_code ec;
        const auto stamp = fs::last_write_time(paths_[i], ec);
        const std::optional<fs::file_time_type> current =
            ec ? std::nullopt : std::optional{stamp};
        if (current != stamps_[i]) {
            changed = true;
            stamps_[i] = current;
        }
    }
    return changed;
}

bool SourceWatch::changed()
{
    if (!inotify_.valid()) {
        return stamps_changed();
    }

    // Одне збереження файлу редактором дає кілька подій — вичитуємо чергу до
    // кінця й повертаємо один-єдиний факт «змінилося».
    alignas(inotify_event) std::array<std::byte, 4096> buffer{};
    bool any = false;
    for (;;) {
        const ssize_t n = ::read(inotify_.get(), buffer.data(), buffer.size());
        if (n > 0) {
            any = true;
            continue;
        }
        if (n < 0 && errno == EINTR) {
            continue;
        }
        if (n < 0 && errno != EAGAIN && errno != EWOULDBLOCK) {
            std::cerr << std::format("minicron: read inotify: {}\n", std::strerror(errno));
        }
        break;
    }
    return any;
}

}  // namespace minicron
