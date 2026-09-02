// substitution.hpp — команда s/РЕГВИРАЗ/ЗАМІНА/ПРАПОРЦІ поверх std::regex.
//
// Шаблон компілюється один раз (конструктор std::regex), у гарячому циклі
// лишається саме зіставлення. Помилка розбору — не -1 і не errno, а
// std::expected із текстом для користувача.
#pragma once

#include <cctype>
#include <cstddef>
#include <expected>
#include <regex>
#include <string>
#include <string_view>
#include <utility>

namespace minised {

class Substitution {
public:
    static std::expected<Substitution, std::string> compile(std::string_view spec,
                                                            bool extended);

    // true — була хоча б одна заміна (той самий брудний біт, що читають t і T).
    bool apply(std::string& ps) const;
    [[nodiscard]] bool print_flag() const noexcept { return print_; }

private:
    Substitution() = default;

    static std::string_view scan_field(std::string_view src, char delim,
                                       std::string& out);
    void expand(const std::smatch& m, std::string& out) const;

    std::regex re_;
    std::string replacement_;   // сире поле: &, \1..\9, \n, \U, \L, \u, \l, \E
    bool global_{false};
    unsigned occurrence_{0};
    bool print_{false};
};

// --- реалізація ------------------------------------------------------------

// Копіює поле до неекранованого роздільника й повертає залишок після нього;
// view з data() == nullptr означає незакрите поле.
inline std::string_view Substitution::scan_field(std::string_view src, char delim,
                                                 std::string& out) {
    for (std::size_t i = 0; i < src.size(); ++i) {
        if (src[i] == '\\' && i + 1 < src.size()) {
            if (src[i + 1] == delim) out += delim;         // \/ — звичайний /
            else { out += src[i]; out += src[i + 1]; }     // решту лишаємо рушію
            ++i;
            continue;
        }
        if (src[i] == delim) return src.substr(i + 1);
        out += src[i];
    }
    return {};
}

inline std::expected<Substitution, std::string> Substitution::compile(
        std::string_view spec, bool extended) {
    if (spec.size() < 2 || spec.front() != 's')
        return std::unexpected("очікувалась команда s/РЕГВИРАЗ/ЗАМІНА/");
    const char delim = spec[1];
    if (delim == '\\' || delim == '\n')
        return std::unexpected("неприпустимий роздільник команди s");

    std::string pattern;
    std::string_view rest = scan_field(spec.substr(2), delim, pattern);
    if (rest.data() == nullptr) return std::unexpected("незакритий регулярний вираз");

    Substitution s;
    rest = scan_field(rest, delim, s.replacement_);
    if (rest.data() == nullptr) return std::unexpected("незакрите поле заміни");

    bool icase = false;
    for (std::size_t i = 0; i < rest.size(); ++i) {
        const char f = rest[i];
        if (f == 'g') s.global_ = true;
        else if (f == 'p') s.print_ = true;
        else if (f == 'I' || f == 'i') icase = true;
        else if (std::isdigit(static_cast<unsigned char>(f))) {
            unsigned n = 0;
            while (i < rest.size() && std::isdigit(static_cast<unsigned char>(rest[i])))
                n = n * 10 + static_cast<unsigned>(rest[i++] - '0');
            --i;
            if (n == 0) return std::unexpected("номер входження мусить бути більший за нуль");
            s.occurrence_ = n;
        } else {
            return std::unexpected(std::string{"невідомий прапорець команди s: "} + f);
        }
    }

    auto grammar = extended ? std::regex::extended : std::regex::basic;
    if (icase) grammar |= std::regex::icase;
    try {
        s.re_.assign(pattern, grammar);
    } catch (const std::regex_error& e) {
        return std::unexpected(std::string{"не компілюється регулярний вираз: "} + e.what());
    }
    return s;
}

inline void Substitution::expand(const std::smatch& m, std::string& out) const {
    char all = 0;   // \U або \L — до \E
    char one = 0;   // \u або \l — рівно на наступний символ
    auto put = [&](char c) {
        auto ch = static_cast<unsigned char>(c);
        if (one) {
            ch = (one == 'u') ? static_cast<unsigned char>(std::toupper(ch))
                              : static_cast<unsigned char>(std::tolower(ch));
            one = 0;
        } else if (all) {
            ch = (all == 'U') ? static_cast<unsigned char>(std::toupper(ch))
                              : static_cast<unsigned char>(std::tolower(ch));
        }
        out += static_cast<char>(ch);
    };
    // string_view з пари ітераторів — конструктор C++20; копії підрядка немає.
    auto put_group = [&](const std::ssub_match& sm) {
        for (char c : std::string_view{sm.first, sm.second}) put(c);
    };

    for (std::size_t i = 0; i < replacement_.size(); ++i) {
        const char c = replacement_[i];
        if (c == '&') {                                     // увесь збіг
            put_group(m[0]);
            continue;
        }
        if (c != '\\' || i + 1 >= replacement_.size()) {
            put(c);
            continue;
        }
        const char e = replacement_[++i];
        if (e >= '0' && e <= '9') {                          // зворотне посилання
            const auto g = static_cast<std::size_t>(e - '0');
            if (g < m.size() && m[g].matched) put_group(m[g]);
            continue;
        }
        switch (e) {
            case 'n': put('\n'); break;
            case 't': put('\t'); break;
            case 'U': case 'L': all = e; one = 0; break;
            case 'u': case 'l': one = e; break;
            case 'E': all = 0; one = 0; break;
            default:  put(e); break;                          // \\ , \& , \/
        }
    }
}

inline bool Substitution::apply(std::string& ps) const {
    const unsigned first = occurrence_ ? occurrence_ : 1;
    unsigned seen = 0;
    bool changed = false;
    std::string out;
    out.reserve(ps.size());
    std::size_t last = 0;

    for (auto it = std::sregex_iterator(ps.begin(), ps.end(), re_),
              end = std::sregex_iterator(); it != end; ++it) {
        const std::smatch& m = *it;
        ++seen;
        const auto pos = static_cast<std::size_t>(m.position(0));
        const auto len = static_cast<std::size_t>(m.length(0));
        out.append(ps, last, pos - last);
        if (seen == first || (global_ && seen > first)) {
            expand(m, out);
            changed = true;
        } else {
            out.append(ps, pos, len);
        }
        last = pos + len;
        if (!global_ && seen >= first) break;
    }

    if (!changed) return false;
    out.append(ps, last, std::string::npos);
    ps = std::move(out);
    return true;
}

}  // namespace minised
