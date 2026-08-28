#include <iostream>
#include <string>
#include <string_view>
#include <cctype>
#include <cstring>
#include <compare>
#include <algorithm>

class CiString {
    std::string str;

    // Швидке посимвольне порівняння без урахування регістру ASCII
    static int char_case_cmp(char a, char b) noexcept {
        auto ua = static_cast<unsigned char>(a);
        auto ub = static_cast<unsigned char>(b);
        int ca = std::tolower(ua);
        int cb = std::tolower(ub);
        return (ca > cb) - (ca < cb);
    }

public:
    CiString() = default;
    CiString(std::string s) : str(std::move(s)) {}
    CiString(const char* s) : str(s) {}

    const std::string& get() const noexcept { return str; }
    std::string_view view() const noexcept { return str; }
    size_t size() const noexcept { return str.size(); }

    // 1. Оптимізована перевірка рівності: O(1) за розміром, далі O(N)
    bool operator==(const CiString& other) const noexcept {
        if (str.size() != other.str.size()) {
            return false;
        }
        for (size_t i = 0; i < str.size(); ++i) {
            if (std::tolower(static_cast<unsigned char>(str[i])) !=
                std::tolower(static_cast<unsigned char>(other.str[i]))) {
                return false;
            }
        }
        return true;
    }

    // 2. Тричленне порівняння слабкого порядку
    std::weak_ordering operator<=>(const CiString& other) const noexcept {
        size_t min_len = std::min(str.size(), other.str.size());
        for (size_t i = 0; i < min_len; ++i) {
            int diff = char_case_cmp(str[i], other.str[i]);
            if (diff < 0) return std::weak_ordering::less;
            if (diff > 0) return std::weak_ordering::greater;
        }
        // Якщо спільний префікс збігся, коротший рядок іде раніше
        return str.size() <=> other.str.size();
    }
};
