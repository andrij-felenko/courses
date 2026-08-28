// ============================================================================
// rrule_spec.hpp — еталонний C++20 парсер, валідатор та генератор RRULE
// ============================================================================
#include <string>
#include <string_view>
#include <array>
#include <vector>
#include <optional>
#include <expected>
#include <cstdint>
#include <algorithm>
#include <charconv>
#include <format>
#include <sstream>

namespace rrule_api {

enum class Freq : uint8_t {
    Unset = 0, Secondly, Minutely, Hourly, Daily, Weekly, Monthly, Yearly
};

enum class Weekday : uint8_t {
    SU = 0, MO = 1, TU = 2, WE = 3, TH = 4, FR = 5, SA = 6
};

enum class ErrorCode {
    EmptyInput,
    InvalidSyntax,
    MissingFreq,
    FreqNotFirst,
    DuplicatePart,
    MutualUntilCount,
    InvalidInterval,
    InvalidCount,
    InvalidUntil,
    InvalidByMonth,
    InvalidByMonthDay,
    InvalidByDay,
    InvalidBySetPos,
    InvalidWkst,
    BySetPosWithoutBy,
    ByMonthDayOnWeekly,
    OrdinalByDayInvalidFreq,
    BufferTooSmall
};

struct WeekdayNum {
    int8_t ord{0}; // 0 = кожен, +1..+53, -53..-1
    Weekday wday{Weekday::MO};
};

struct RuleSpec {
    Freq freq{Freq::Unset};
    uint32_t interval{1};
    std::optional<uint32_t> count{std::nullopt};
    std::optional<std::string> until{std::nullopt};
    uint16_t bymonth_mask{0};
    uint32_t bymonthday_pos_mask{0};
    uint32_t bymonthday_neg_mask{0};
    std::vector<WeekdayNum> byday{};
    std::vector<int16_t> bysetpos{};
    Weekday wkst{Weekday::MO};

    [[nodiscard]] constexpr bool has_by_filters() const noexcept {
        return (bymonth_mask != 0) || (bymonthday_pos_mask != 0) ||
               (bymonthday_neg_mask != 0) || (!byday.empty());
    }
};

class RRuleParser {
public:
    static constexpr std::string_view freq_to_string(Freq f) noexcept {
        switch (f) {
            case Freq::Secondly: return "SECONDLY";
            case Freq::Minutely: return "MINUTELY";
            case Freq::Hourly:   return "HOURLY";
            case Freq::Daily:    return "DAILY";
            case Freq::Weekly:   return "WEEKLY";
            case Freq::Monthly:  return "MONTHLY";
            case Freq::Yearly:   return "YEARLY";
            default:             return "";
        }
    }

    static constexpr std::string_view wday_to_string(Weekday w) noexcept {
        switch (w) {
            case Weekday::SU: return "SU";
            case Weekday::MO: return "MO";
            case Weekday::TU: return "TU";
            case Weekday::WE: return "WE";
            case Weekday::TH: return "TH";
            case Weekday::FR: return "FR";
            case Weekday::SA: return "SA";
        }
        return "MO";
    }

    static constexpr std::optional<Weekday> parse_wday(std::string_view sv) noexcept {
        if (sv == "SU") return Weekday::SU;
        if (sv == "MO") return Weekday::MO;
        if (sv == "TU") return Weekday::TU;
        if (sv == "WE") return Weekday::WE;
        if (sv == "TH") return Weekday::TH;
        if (sv == "FR") return Weekday::FR;
        if (sv == "SA") return Weekday::SA;
        return std::nullopt;
    }

    static std::expected<RuleSpec, ErrorCode> parse(std::string_view input) noexcept {
        if (input.empty()) return std::unexpected(ErrorCode::EmptyInput);
        if (input.starts_with("RRULE:")) input.remove_prefix(6);

        RuleSpec spec{};
        bool is_first = true;
        uint32_t seen_mask = 0;

        while (!input.empty()) {
            size_t semi = input.find(';');
            std::string_view part = (semi == std::string_view::npos) ? input : input.substr(0, semi);
            input = (semi == std::string_view::npos) ? std::string_view{} : input.substr(semi + 1);

            size_t eq = part.find('=');
            if (eq == std::string_view::npos) return std::unexpected(ErrorCode::InvalidSyntax);
            std::string_view key = part.substr(0, eq);
            std::string_view val = part.substr(eq + 1);
            if (val.empty()) return std::unexpected(ErrorCode::InvalidSyntax);

            if (key == "FREQ") {
                if (!is_first) return std::unexpected(ErrorCode::FreqNotFirst);
                if (seen_mask & (1 << 0)) return std::unexpected(ErrorCode::DuplicatePart);
                seen_mask |= (1 << 0);

                if (val == "SECONDLY") spec.freq = Freq::Secondly;
                else if (val == "MINUTELY") spec.freq = Freq::Minutely;
                else if (val == "HOURLY") spec.freq = Freq::Hourly;
                else if (val == "DAILY") spec.freq = Freq::Daily;
                else if (val == "WEEKLY") spec.freq = Freq::Weekly;
                else if (val == "MONTHLY") spec.freq = Freq::Monthly;
                else if (val == "YEARLY") spec.freq = Freq::Yearly;
                else return std::unexpected(ErrorCode::InvalidSyntax);
            } else if (key == "INTERVAL") {
                if (seen_mask & (1 << 1)) return std::unexpected(ErrorCode::DuplicatePart);
                seen_mask |= (1 << 1);
                uint32_t iv = 0;
                auto [p, ec] = std::from_chars(val.data(), val.data() + val.size(), iv);
                if (ec != std::errc{} || p != val.data() + val.size() || iv == 0) {
                    return std::unexpected(ErrorCode::InvalidInterval);
                }
                spec.interval = iv;
            } else if (key == "COUNT") {
                if (seen_mask & (1 << 2)) return std::unexpected(ErrorCode::DuplicatePart);
                seen_mask |= (1 << 2);
                uint32_t cnt = 0;
                auto [p, ec] = std::from_chars(val.data(), val.data() + val.size(), cnt);
                if (ec != std::errc{} || p != val.data() + val.size() || cnt == 0) {
                    return std::unexpected(ErrorCode::InvalidCount);
                }
                spec.count = cnt;
            } else if (key == "UNTIL") {
                if (seen_mask & (1 << 3)) return std::unexpected(ErrorCode::DuplicatePart);
                seen_mask |= (1 << 3);
                if (val.size() < 8) return std::unexpected(ErrorCode::InvalidUntil);
                if (val.size() > 8 && !val.ends_with('Z')) return std::unexpected(ErrorCode::InvalidUntil);
                spec.until = std::string(val);
            } else if (key == "BYMONTH") {
                if (seen_mask & (1 << 4)) return std::unexpected(ErrorCode::DuplicatePart);
                seen_mask |= (1 << 4);
                std::string_view remaining = val;
                while (!remaining.empty()) {
                    size_t comma = remaining.find(',');
                    std::string_view token = (comma == std::string_view::npos) ? remaining : remaining.substr(0, comma);
                    remaining = (comma == std::string_view::npos) ? std::string_view{} : remaining.substr(comma + 1);

                    int m = 0;
                    auto [p, ec] = std::from_chars(token.data(), token.data() + token.size(), m);
                    if (ec != std::errc{} || p != token.data() + token.size() || m < 1 || m > 12) {
                        return std::unexpected(ErrorCode::InvalidByMonth);
                    }
                    spec.bymonth_mask |= (1 << m);
                }
            } else if (key == "BYMONTHDAY") {
                if (seen_mask & (1 << 5)) return std::unexpected(ErrorCode::DuplicatePart);
                seen_mask |= (1 << 5);
                std::string_view remaining = val;
                while (!remaining.empty()) {
                    size_t comma = remaining.find(',');
                    std::string_view token = (comma == std::string_view::npos) ? remaining : remaining.substr(0, comma);
                    remaining = (comma == std::string_view::npos) ? std::string_view{} : remaining.substr(comma + 1);

                    int md = 0;
                    auto [p, ec] = std::from_chars(token.data(), token.data() + token.size(), md);
                    if (ec != std::errc{} || p != token.data() + token.size() || md == 0 || md < -31 || md > 31) {
                        return std::unexpected(ErrorCode::InvalidByMonthDay);
                    }
                    if (md > 0) spec.bymonthday_pos_mask |= (1U << md);
                    else spec.bymonthday_neg_mask |= (1U << (-md));
                }
            } else if (key == "BYDAY") {
                if (seen_mask & (1 << 6)) return std::unexpected(ErrorCode::DuplicatePart);
                seen_mask |= (1 << 6);
                std::string_view remaining = val;
                while (!remaining.empty()) {
                    size_t comma = remaining.find(',');
                    std::string_view token = (comma == std::string_view::npos) ? remaining : remaining.substr(0, comma);
                    remaining = (comma == std::string_view::npos) ? std::string_view{} : remaining.substr(comma + 1);

                    int8_t ord = 0;
                    std::string_view wstr = token;
                    if (token.size() > 2) {
                        int ord_val = 0;
                        auto [p, ec] = std::from_chars(token.data(), token.data() + token.size() - 2, ord_val);
                        if (ec != std::errc{} || p != token.data() + token.size() - 2 || ord_val < -53 || ord_val > 53 || ord_val == 0) {
                            return std::unexpected(ErrorCode::InvalidByDay);
                        }
                        ord = static_cast<int8_t>(ord_val);
                        wstr = token.substr(token.size() - 2);
                    }
                    auto wd_opt = parse_wday(wstr);
                    if (!wd_opt) return std::unexpected(ErrorCode::InvalidByDay);
                    spec.byday.push_back(WeekdayNum{ord, *wd_opt});
                }
            } else if (key == "BYSETPOS") {
                if (seen_mask & (1 << 7)) return std::unexpected(ErrorCode::DuplicatePart);
                seen_mask |= (1 << 7);
                std::string_view remaining = val;
                while (!remaining.empty()) {
                    size_t comma = remaining.find(',');
                    std::string_view token = (comma == std::string_view::npos) ? remaining : remaining.substr(0, comma);
                    remaining = (comma == std::string_view::npos) ? std::string_view{} : remaining.substr(comma + 1);

                    int sp = 0;
                    auto [p, ec] = std::from_chars(token.data(), token.data() + token.size(), sp);
                    if (ec != std::errc{} || p != token.data() + token.size() || sp == 0 || sp < -366 || sp > 366) {
                        return std::unexpected(ErrorCode::InvalidBySetPos);
                    }
                    spec.bysetpos.push_back(static_cast<int16_t>(sp));
                }
            } else if (key == "WKST") {
                if (seen_mask & (1 << 8)) return std::unexpected(ErrorCode::DuplicatePart);
                seen_mask |= (1 << 8);
                auto wd_opt = parse_wday(val);
                if (!wd_opt) return std::unexpected(ErrorCode::InvalidWkst);
                spec.wkst = *wd_opt;
            }

            is_first = false;
        }

        return validate(spec);
    }

    static std::expected<RuleSpec, ErrorCode> validate(const RuleSpec& spec) noexcept {
        if (spec.freq == Freq::Unset) return std::unexpected(ErrorCode::MissingFreq);
        if (spec.count.has_value() && spec.until.has_value()) return std::unexpected(ErrorCode::MutualUntilCount);
        if (spec.interval == 0) return std::unexpected(ErrorCode::InvalidInterval);

        if (spec.freq == Freq::Weekly && (spec.bymonthday_pos_mask || spec.bymonthday_neg_mask)) {
            return std::unexpected(ErrorCode::ByMonthDayOnWeekly);
        }

        if (!spec.bysetpos.empty() && !spec.has_by_filters()) {
            return std::unexpected(ErrorCode::BySetPosWithoutBy);
        }

        for (const auto& d : spec.byday) {
            if (d.ord != 0 && spec.freq != Freq::Monthly && spec.freq != Freq::Yearly) {
                return std::unexpected(ErrorCode::OrdinalByDayInvalidFreq);
            }
        }

        return spec;
    }

    static std::string to_string(const RuleSpec& spec) {
        std::ostringstream ss;
        ss << "FREQ=" << freq_to_string(spec.freq);

        if (spec.interval > 1) ss << ";INTERVAL=" << spec.interval;
        if (spec.count.has_value()) ss << ";COUNT=" << *spec.count;
        else if (spec.until.has_value()) ss << ";UNTIL=" << *spec.until;

        if (spec.bymonth_mask != 0) {
            ss << ";BYMONTH=";
            bool first = true;
            for (int m = 1; m <= 12; ++m) {
                if (spec.bymonth_mask & (1 << m)) {
                    if (!first) ss << ',';
                    ss << m;
                    first = false;
                }
            }
        }

        if (spec.bymonthday_pos_mask || spec.bymonthday_neg_mask) {
            ss << ";BYMONTHDAY=";
            bool first = true;
            for (int d = 1; d <= 31; ++d) {
                if (spec.bymonthday_pos_mask & (1U << d)) {
                    if (!first) ss << ',';
                    ss << d;
                    first = false;
                }
            }
            for (int d = 1; d <= 31; ++d) {
                if (spec.bymonthday_neg_mask & (1U << d)) {
                    if (!first) ss << ',';
                    ss << '-' << d;
                    first = false;
                }
            }
        }

        if (!spec.byday.empty()) {
            ss << ";BYDAY=";
            for (size_t i = 0; i < spec.byday.size(); ++i) {
                if (i > 0) ss << ',';
                if (spec.byday[i].ord != 0) ss << static_cast<int>(spec.byday[i].ord);
                ss << wday_to_string(spec.byday[i].wday);
            }
        }

        if (!spec.bysetpos.empty()) {
            ss << ";BYSETPOS=";
            for (size_t i = 0; i < spec.bysetpos.size(); ++i) {
                if (i > 0) ss << ',';
                ss << spec.bysetpos[i];
            }
        }

        if (spec.wkst != Weekday::MO) {
            ss << ";WKST=" << wday_to_string(spec.wkst);
        }

        return ss.str();
    }
};

} // namespace rrule_api
