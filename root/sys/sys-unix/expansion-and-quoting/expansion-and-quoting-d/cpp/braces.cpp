#include "braces.hpp"

#include "expansion.hpp"
#include "quoting.hpp"

#include <algorithm>
#include <charconv>
#include <limits>
#include <optional>

#include <wordexp.h>   // заради кодів WRDE_* у expand_error

namespace shexp {
namespace {

constexpr std::size_t npos = std::string_view::npos;

// Дужки множаться комбінаторно: {1..99}{1..99} це майже десять тисяч слів.
constexpr std::size_t kLimit = 4096;

[[noreturn]] void too_many()
{
    // Свого коду для «забагато слів» у wordexp(3) немає, а сенс WRDE_NOSPACE
    // саме такий: вектор слів не вміщується.
    throw expand_error{WRDE_NOSPACE, "запис породжує забагато слів"};
}

std::size_t find_open(std::string_view s)
{
    for (std::size_t i = 0; i < s.size();) {
        const std::size_t next = skip_quoted(s, i);
        if (next == i + 1 && s[i] == '{') {
            return i;
        }
        i = next;
    }
    return npos;
}

std::size_t match_close(std::string_view s, std::size_t open)
{
    int depth = 0;
    for (std::size_t i = open; i < s.size();) {
        const std::size_t next = skip_quoted(s, i);
        if (next == i + 1) {
            if (s[i] == '{') {
                ++depth;
            } else if (s[i] == '}' && --depth == 0) {
                return i;
            }
        }
        i = next;
    }
    return npos;
}

// Кома всередині вкладених дужок чи в лапках роздільником не є.
std::vector<std::string_view> split_commas(std::string_view body)
{
    std::vector<std::string_view> parts;
    int depth = 0;
    std::size_t start = 0;

    for (std::size_t i = 0; i < body.size();) {
        const std::size_t next = skip_quoted(body, i);
        if (next == i + 1) {
            if (body[i] == '{') {
                ++depth;
            } else if (body[i] == '}') {
                --depth;
            } else if (body[i] == ',' && depth == 0) {
                parts.push_back(body.substr(start, i - start));
                start = i + 1;
            }
        }
        i = next;
    }
    parts.push_back(body.substr(start));
    return parts;
}

std::optional<long> to_long(std::string_view s)
{
    long value = 0;
    const auto [stop, ec] = std::from_chars(s.data(), s.data() + s.size(), value);
    // Діапазоном вважаємо лише те, що розібралося ЦІЛКОМ: «1x» це текст.
    if (ec != std::errc{} || stop != s.data() + s.size()) {
        return std::nullopt;
    }
    return value;
}

bool has_leading_zero(std::string_view s)
{
    if (!s.empty() && s.front() == '-') {
        s.remove_prefix(1);
    }
    return s.size() > 1 && s.front() == '0';
}

// {01..05}: провідний нуль бодай з одного боку вирівнює всі числа нулями.
std::string pad(long value, std::size_t width)
{
    const unsigned long magnitude = (value < 0)
        ? 0UL - static_cast<unsigned long>(value)
        : static_cast<unsigned long>(value);

    std::string digits = std::to_string(magnitude);
    const std::string sign = (value < 0) ? "-" : "";

    if (digits.size() + sign.size() < width) {
        digits.insert(0, width - digits.size() - sign.size(), '0');
    }
    return sign + digits;
}

std::optional<std::vector<std::string>> numeric_range(long from, long to, long step,
                                                      std::size_t width)
{
    const unsigned long mag = (step < 0)
        ? 0UL - static_cast<unsigned long>(step)
        : static_cast<unsigned long>(step);
    if (mag == 0 || mag > static_cast<unsigned long>(std::numeric_limits<long>::max())) {
        return std::nullopt;   // {1..5..0} діапазоном не є — лишиться текстом
    }

    // Різницю рахуємо беззнаковою: інакше {-9223372036854775808..0}
    // переповнив би long ще до першого кроку.
    const unsigned long span = (from <= to)
        ? static_cast<unsigned long>(to) - static_cast<unsigned long>(from)
        : static_cast<unsigned long>(from) - static_cast<unsigned long>(to);

    const unsigned long steps = span / mag;
    if (steps + 1 > kLimit) {
        too_many();
    }

    const long inc = (from <= to) ? static_cast<long>(mag) : -static_cast<long>(mag);
    std::vector<std::string> out;
    out.reserve(static_cast<std::size_t>(steps) + 1);

    long value = from;
    for (unsigned long k = 0; k <= steps; ++k) {
        out.push_back(pad(value, width));
        if (k < steps) {
            value += inc;   // останній крок не робимо: він міг би переповнити
        }
    }
    return out;
}

std::optional<std::vector<std::string>> char_range(char from, char to, long step)
{
    const long mag = (step < 0) ? -step : step;
    if (mag == 0 || mag > 255) {
        return std::nullopt;
    }
    const long inc = (from <= to) ? mag : -mag;

    std::vector<std::string> out;
    for (long c = from; (inc > 0) ? (c <= to) : (c >= to); c += inc) {
        out.emplace_back(1, static_cast<char>(c));
    }
    return out;
}

std::optional<std::vector<std::string>> parse_range(std::string_view body)
{
    // Лапки й екрани означають, що це звичайний текст, а не діапазон.
    if (body.find_first_of("'\"\\") != npos) {
        return std::nullopt;
    }

    std::vector<std::string_view> segs;
    std::size_t start = 0;
    for (std::size_t i = 0; i + 1 < body.size();) {
        if (body[i] == '.' && body[i + 1] == '.') {
            segs.push_back(body.substr(start, i - start));
            i += 2;
            start = i;
        } else {
            ++i;
        }
    }
    segs.push_back(body.substr(start));

    if (segs.size() < 2 || segs.size() > 3 || segs[0].empty() || segs[1].empty()) {
        return std::nullopt;
    }

    long step = 1;
    if (segs.size() == 3) {
        const auto parsed = to_long(segs[2]);
        if (!parsed) {
            return std::nullopt;
        }
        step = *parsed;
    }

    const auto from = to_long(segs[0]);
    const auto to = to_long(segs[1]);
    if (from && to) {
        const std::size_t width = (has_leading_zero(segs[0]) || has_leading_zero(segs[1]))
            ? std::max(segs[0].size(), segs[1].size())
            : 0;
        return numeric_range(*from, *to, step, width);
    }
    if (segs[0].size() == 1 && segs[1].size() == 1) {
        return char_range(segs[0][0], segs[1][0], step);
    }
    return std::nullopt;
}

void expand_into(std::string_view word, std::vector<std::string>& out)
{
    if (out.size() >= kLimit) {
        too_many();
    }

    const std::size_t open = find_open(word);
    const std::size_t close = (open == npos) ? npos : match_close(word, open);
    if (close == npos) {
        // Ні дужок, ні закритої пари — слово йде далі як є.
        out.emplace_back(word);
        return;
    }

    const std::string_view pre = word.substr(0, open);
    const std::string_view body = word.substr(open + 1, close - open - 1);

    // Хвіст після '}' розгортається сам по собі: {a,b}{1,2} дає добуток.
    std::vector<std::string> posts;
    expand_into(word.substr(close + 1), posts);

    std::vector<std::string> mids;
    bool is_list = false;

    if (auto range = parse_range(body)) {
        mids = std::move(*range);
        is_list = true;
    } else if (const auto parts = split_commas(body); parts.size() >= 2) {
        is_list = true;
        for (std::string_view part : parts) {
            expand_into(part, mids);   // частина теж може мати свої дужки
        }
    }

    if (!is_list) {
        // Ні коми, ні діапазону: дужки лишаються буквально, але вміст усе
        // одно проходить фазу. Так поводиться й Bash — {single} лишається
        // собою, а {a{b,c}} дає {ab} {ac}.
        std::vector<std::string> inner;
        expand_into(body, inner);
        mids.clear();
        for (const std::string& piece : inner) {
            mids.push_back(std::string{'{'} + piece + '}');
        }
    }

    for (const std::string& mid : mids) {
        for (const std::string& post : posts) {
            if (out.size() >= kLimit) {
                too_many();
            }
            out.push_back(std::string{pre} + mid + post);
        }
    }
}

}  // namespace

std::vector<std::string> expand_braces(std::string_view word)
{
    std::vector<std::string> out;
    expand_into(word, out);
    return out;
}

}  // namespace shexp
