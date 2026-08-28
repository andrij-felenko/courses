#include <iostream>
#include <string_view>
#include <vector>
#include <cstdint>
#include <algorithm>

struct Interval {
    uint32_t first;
    uint32_t last;
};

// Швидкий бінарний пошук за інтервалами кодових позицій
bool in_intervals(uint32_t cp, const std::vector<Interval>& table) {
    if (table.empty() || cp < table.front().first || cp > table.back().last) {
        return false;
    }
    auto it = std::lower_bound(table.begin(), table.end(), cp,
        [](const Interval& interval, uint32_t val) {
            return interval.last < val;
        });
    return (it != table.end() && cp >= it->first && cp <= it->last);
}

bool is_zero_width(uint32_t cp) {
    static const std::vector<Interval> zero_table = {
        {0x0000, 0x0000},
        {0x0300, 0x036F}, // Combining Diacritical Marks
        {0x0483, 0x0489}, // Cyrillic Combining Marks
        {0x0591, 0x05BD}, // Hebrew Accents
        {0x05BF, 0x05BF},
        {0x05C1, 0x05C2},
        {0x05C4, 0x05C5},
        {0x05C7, 0x05C7},
        {0x0610, 0x061A}, // Arabic Signs
        {0x064B, 0x065F},
        {0x0670, 0x0670},
        {0x06D6, 0x06DC},
        {0x200B, 0x200F}, // ZWSP, ZWNJ, ZWJ, LRM, RLM
        {0x202A, 0x202E}, // BiDi Controls
        {0x2060, 0x206F}, // Formatting
        {0xFE00, 0xFE0F}, // Variation Selectors
        {0xE0100, 0xE01EF}
    };
    return in_intervals(cp, zero_table);
}

bool is_wide_char(uint32_t cp) {
    static const std::vector<Interval> wide_table = {
        {0x1100, 0x115F},   // Hangul Jamo
        {0x231A, 0x231B},   // Watch, Hourglass
        {0x23E9, 0x23EC},
        {0x23F0, 0x23F3},
        {0x25FD, 0x25FE},
        {0x2614, 0x2615},
        {0x2648, 0x2653},
        {0x267F, 0x267F},
        {0x2693, 0x2693},
        {0x26A1, 0x26A1},
        {0x26AA, 0x26AB},
        {0x26BD, 0x26BE},
        {0x26C4, 0x26C5},
        {0x26CE, 0x26CE},
        {0x26D4, 0x26D4},
        {0x26EA, 0x26EA},
        {0x26F2, 0x26F3},
        {0x26F5, 0x26F5},
        {0x26FA, 0x26FA},
        {0x26FD, 0x26FD},
        {0x2705, 0x2705},
        {0x270A, 0x270B},
        {0x2728, 0x2728},
        {0x274C, 0x274C},
        {0x274E, 0x274E},
        {0x2753, 0x2755},
        {0x2757, 0x2757},
        {0x27B0, 0x27B0},
        {0x27BF, 0x27BF},
        {0x2B1B, 0x2B1C},
        {0x2B50, 0x2B50},
        {0x2B55, 0x2B55},
        {0x2E80, 0xA4CF},   // CJK Radicals, Ideographs
        {0xAC00, 0xD7A3},   // Hangul Syllables
        {0xF900, 0xFAFF},   // CJK Compatibility
        {0xFE10, 0xFE19},
        {0xFE30, 0xFE6F},
        {0xFF01, 0xFF60},   // Fullwidth ASCII
        {0xFFE0, 0xFFE6},
        {0x1F300, 0x1F64F}, // Emoji
        {0x1F680, 0x1F6FF},
        {0x1F900, 0x1F9FF},
        {0x1FA70, 0x1FAFF},
        {0x20000, 0x3FFFD}  // CJK Unified Extensions
    };
    return in_intervals(cp, wide_table);
}

// Декодування наступного UTF-8 символу з перевіркою коректності
std::pair<uint32_t, std::size_t> decode_utf8(std::string_view s) {
    if (s.empty()) return {0, 0};
    auto c = static_cast<unsigned char>(s[0]);

    if (c < 0x80) {
        return {c, 1};
    } else if ((c & 0xE0) == 0xC0 && s.size() >= 2) {
        return {((c & 0x1F) << 6) | (s[1] & 0x3F), 2};
    } else if ((c & 0xF0) == 0xE0 && s.size() >= 3) {
        return {((c & 0x0F) << 12) | ((s[1] & 0x3F) << 6) | (s[2] & 0x3F), 3};
    } else if ((c & 0xF8) == 0xF0 && s.size() >= 4) {
        return {((c & 0x07) << 18) | ((s[1] & 0x3F) << 12) | ((s[2] & 0x3F) << 6) | (s[3] & 0x3F), 4};
    }
    return {0xFFFD, 1};
}

int calculate_grapheme_string_width(std::string_view utf8_str) {
    std::size_t offset = 0;
    int total_width = 0;
    int current_cluster_width = 0;
    bool in_zwj_sequence = false;
    bool is_regional_indicator = false;

    while (offset < utf8_str.size()) {
        auto [cp, bytes] = decode_utf8(utf8_str.substr(offset));
        if (bytes == 0) break;
        offset += bytes;

        if (cp == 0x200D) { // ZWJ
            in_zwj_sequence = true;
            continue;
        }

        if (cp == 0xFE0E) { // VS15
            if (current_cluster_width > 1) current_cluster_width = 1;
            continue;
        }
        if (cp == 0xFE0F) { // VS16
            if (current_cluster_width < 2) current_cluster_width = 2;
            continue;
        }

        if (is_zero_width(cp)) {
            continue;
        }

        if (cp >= 0x1F1E6 && cp <= 0x1F1FF) {
            if (is_regional_indicator) {
                is_regional_indicator = false;
                continue;
            } else {
                total_width += current_cluster_width;
                current_cluster_width = 2;
                is_regional_indicator = true;
                continue;
            }
        }
        is_regional_indicator = false;

        if (in_zwj_sequence) {
            in_zwj_sequence = false;
            if (current_cluster_width < 2) current_cluster_width = 2;
            continue;
        }

        total_width += current_cluster_width;
        current_cluster_width = is_wide_char(cp) ? 2 : 1;
    }

    total_width += current_cluster_width;
    return total_width;
}

int main() {
    const std::vector<std::string_view> test_cases = {
        "ASCII text",
        "Кирилиця",
        "Кава ☕ та код 💻",
        "е\u0301кран (accent)",
        "👨‍💻 програміст",
        "🇺🇦 Україна"
    };

    for (const auto& text : test_cases) {
        int w = calculate_grapheme_string_width(text);
        std::cout << "Рядок: " << text << " | Ширина: " << w << " комірок\n";
    }

    return 0;
}
