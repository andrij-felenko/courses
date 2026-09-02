// main.cpp — межі аргументів після розгортання, очима програми.
// Без аргументів іде вбудований набір прикладів; з аргументами —
// розгортається кожен переданий рядок.
//
// Збірка: c++ -std=c++20 -Wall -Wextra -o expand main.cpp expansion.cpp
#include "expansion.hpp"

#include <iostream>
#include <span>
#include <string>
#include <string_view>
#include <vector>

namespace {

// Робить видимими символи, які на терміналі зливаються з розміткою виводу.
std::string visible(std::string_view word)
{
    std::string out;
    out.reserve(word.size());
    for (char c : word) {
        if (c == '\n') {
            out += "\\n";
        } else if (c == '\t') {
            out += "\\t";
        } else {
            out += c;
        }
    }
    return out;
}

// Повертає true, якщо рядок розгорнувся.
bool show(std::string_view line)
{
    std::cout << "рядок: " << line << '\n';
    try {
        const std::vector<std::string> words = shexp::expand(line);
        if (words.empty()) {
            std::cout << "  (жодного слова — усе розгорнулося в порожнечу)\n";
        }
        for (std::size_t i = 0; i < words.size(); ++i) {
            std::cout << "  argv[" << i << "] = «" << visible(words[i]) << "»\n";
        }
        std::cout << "  усього слів: " << words.size() << "\n\n";
        return true;
    } catch (const shexp::expand_error& err) {
        std::cerr << "  відхилено (" << err.status() << "): " << err.what() << "\n\n";
        return false;
    }
}

const std::vector<std::string_view>& demo()
{
    static const std::vector<std::string_view> lines{
        "$HOME/*.txt",                 // параметр і глобінг
        "~/.bashrc",                   // розгортання тильди
        "'одне слово з пробілами' і ще два",
        "$((6 * 7)) — відповідь",      // арифметичне розгортання
        "\"$HOME\"/*.txt",             // у лапках глобінгу немає
        "file_{A,B}.txt",              // дужки НЕ POSIX: лишаються буквально
        "$(date)",                     // WRDE_NOCMD: підстановку команди відхилено
        "`date`",                      // застаріла форма блокується так само
        "$NO_SUCH_VAR_12345/архів",    // WRDE_UNDEF: невизначена змінна
        "звіт | wc",                   // WRDE_BADCHAR: метасимвол поза лапками
        "незакрита 'лапка",            // WRDE_SYNTAX
    };
    return lines;
}

}  // namespace

int main(int argc, char** argv)
{
    const std::span<char* const> args{argv, static_cast<std::size_t>(argc)};

    std::vector<std::string_view> lines;
    if (args.size() > 1) {
        lines.assign(args.begin() + 1, args.end());
    } else {
        lines = demo();
    }

    int failures = 0;
    for (std::string_view line : lines) {
        if (!show(line)) {
            ++failures;
        }
    }

    // У вбудованому наборі відмови очікувані — ненульовий статус тут норма.
    return failures > 0 ? 1 : 0;
}
