#include <iostream>
#include <string_view>
#include <vector>
#include <cwchar>
#include <clocale>
#include <cstring>
#include <expected>

enum class StringWidthError {
    InvalidUtf8Sequence,
    IncompleteSequence,
    NonPrintableCharacter
};

// Розрахунок термінальної ширини рядка UTF-8 у стилі C++23 з std::expected
std::expected<int, StringWidthError> calculate_utf8_display_width(std::string_view utf8_text) {
    std::mbstate_t state{};
    const char* current = utf8_text.data();
    std::size_t remaining = utf8_text.size();
    int total_width = 0;

    while (remaining > 0) {
        wchar_t wc = 0;
        std::size_t consumed = std::mbrtowc(&wc, current, remaining, &state);

        if (consumed == 0) {
            break;
        }
        if (consumed == static_cast<std::size_t>(-1)) {
            return std::unexpected(StringWidthError::InvalidUtf8Sequence);
        }
        if (consumed == static_cast<std::size_t>(-2)) {
            return std::unexpected(StringWidthError::IncompleteSequence);
        }

        int w = wcwidth(wc);
        if (w < 0) {
            return std::unexpected(StringWidthError::NonPrintableCharacter);
        }

        total_width += w;
        current += consumed;
        remaining -= consumed;
    }

    return total_width;
}

int main() {
    std::setlocale(LC_CTYPE, "");

    const std::vector<std::string_view> test_lines = {
        "Команда: status",
        "Статус: [OK]",
        "Символи CJK: 言語",
        "Діакритика: е\u0301кран"
    };

    for (const auto& line : test_lines) {
        auto width_result = calculate_utf8_display_width(line);
        if (width_result.has_value()) {
            std::cout << "Текст: " << line << " -> Ширина: " << *width_result << " комірок\n";
        } else {
            std::cerr << "Помилка розрахунку ширини для рядка: " << line << "\n";
        }
    }
    return 0;
}
