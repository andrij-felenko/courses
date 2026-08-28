#include <format>
#include <iostream>
#include <string_view>
#include <type_traits>

consteval std::size_t count_slots(std::string_view s) {
    std::size_t n = 0;
    for (std::size_t i = 0; i < s.size(); ++i) {
        if (s[i] != '{') continue;
        if (i + 1 < s.size() && s[i + 1] == '{') { ++i; continue; }   // «{{» — екранована дужка
        if (i + 1 >= s.size() || s[i + 1] != '}')
            throw "у рядку формату є '{' без пари";
        ++n; ++i;
    }
    return n;
}

template <class... Args>
struct fmt_string {
    std::string_view text;
    consteval fmt_string(const char* s) : text(s) {
        if (count_slots(text) != sizeof...(Args))
            throw "кількість {} не збігається з кількістю аргументів";
    }
};

template <class... Args>
void log(fmt_string<std::type_identity_t<Args>...> f, Args&&... args) {
    std::cout << std::vformat(f.text, std::make_format_args(args...)) << '\n';
}

log("порт {} зайнято процесом {}", 8080, "nginx");   // добре
log("порт {} зайнято процесом {}", 8080);            // помилка компіляції
log("порт {", 8080);                                 // помилка компіляції
