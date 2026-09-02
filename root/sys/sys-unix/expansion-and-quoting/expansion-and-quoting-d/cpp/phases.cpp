// phases.cpp — увесь конвеєр за один прогін: рядок → argv[].
//
// Фаза 1 живе в braces.cpp, фази 2, 3 і 6 — у marked_word.cpp, фаза 4 —
// у fields.cpp, фаза 5 лишилася тут, бо це кілька рядків навколо glob(3).
// Підстановки команд і арифметики свідомо немає: перше запускає процеси,
// друге це окремий обчислювач виразів. Те й те показує приклад на wordexp(3).
//
// Збірка: c++ -std=c++20 -Wall -Wextra -o phases phases.cpp braces.cpp \
//             marked_word.cpp fields.cpp quoting.cpp
// Запуск:  ./phases '$HOME/*.txt'   або ./phases (вбудований набір)
#include "braces.hpp"
#include "expansion.hpp"
#include "fields.hpp"
#include "marked_word.hpp"
#include "quoting.hpp"

#include <cstdlib>
#include <iostream>
#include <span>
#include <string>
#include <string_view>
#include <vector>

#include <glob.h>

namespace {

using shexp::marked_word;

// Власник glob_t: захоплює в конструкторі, звільняє в деструкторі.
class glob_result {
public:
    explicit glob_result(const std::string& pattern)
        // buf_ занулено ще до виклику (ініціалізатор поля), тож globfree(3)
        // безпечний за будь-якого результату glob(3).
        : status_{::glob(pattern.c_str(), 0, nullptr, &buf_)} {}

    ~glob_result() { ::globfree(&buf_); }

    glob_result(const glob_result&) = delete;
    glob_result& operator=(const glob_result&) = delete;

    [[nodiscard]] bool matched() const noexcept { return status_ == 0; }

    [[nodiscard]] std::span<char* const> paths() const noexcept
    {
        return matched() ? std::span<char* const>{buf_.gl_pathv, buf_.gl_pathc}
                         : std::span<char* const>{};
    }

private:
    glob_t buf_{};
    int status_;
};

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

std::string current_ifs()
{
    if (const char* value = std::getenv("IFS")) {
        return std::string{value};
    }
    return std::string{" \t\n"};
}

// Фаза 5. Слово без живих метасимволів іде далі як є — жодного звертання
// до файлової системи для нього не буде.
std::vector<std::string> glob_step(const marked_word& w)
{
    if (!w.has_active("*?[")) {
        return {w.text()};
    }

    const glob_result found{w.glob_pattern()};
    if (!found.matched()) {
        // POSIX: маска без збігів лишається в argv[] сама собою. Саме це
        // поводження міняють shopt -s nullglob і failglob.
        return {w.text()};
    }

    std::vector<std::string> out;
    for (const char* path : found.paths()) {
        out.emplace_back(path);
    }
    return out;
}

// true, якщо рядок пройшов конвеєр без жодної відмови.
bool run(std::string_view line)
{
    std::cout << "рядок: " << line << '\n';

    const std::vector<std::string> raw = shexp::split_words(line);
    std::vector<std::string> braced;
    bool ok = true;

    try {
        for (const std::string& token : raw) {
            const std::vector<std::string> grown = shexp::expand_braces(token);
            braced.insert(braced.end(), grown.begin(), grown.end());
        }
    } catch (const shexp::expand_error& err) {
        std::cout << "  дужки: " << err.what() << "\n\n";
        return false;
    }

    std::cout << "  слів після лексики: " << raw.size()
              << ", після дужок: " << braced.size() << '\n';

    const std::string ifs = current_ifs();
    std::vector<std::string> argv;

    for (const std::string& token : braced) {
        try {
            const marked_word expanded = shexp::expand_word(token);
            for (const marked_word& field : shexp::split_fields(expanded, ifs)) {
                const std::vector<std::string> globbed = glob_step(field);
                argv.insert(argv.end(), globbed.begin(), globbed.end());
            }
        } catch (const shexp::expand_error& err) {
            std::cout << "  «" << token << "» відхилено: " << err.what() << '\n';
            ok = false;
        }
    }

    if (argv.empty()) {
        std::cout << "  (жодного слова — усе розгорнулося в порожнечу)\n";
    }
    for (std::size_t i = 0; i < argv.size(); ++i) {
        std::cout << "  argv[" << i << "] = «" << visible(argv[i]) << "»\n";
    }
    std::cout << "  усього в argv[]: " << argv.size() << "\n\n";
    return ok;
}

const std::vector<std::string_view>& demo()
{
    static const std::vector<std::string_view> lines{
        "file_{A,B}.txt",              // фаза 1: список
        "{src,test}/{main,util}.c",    // добуток двох списків
        "{01..05}",                    // діапазон із шириною поля
        "{a..e}",                      // символьний діапазон
        "{single} {a{b,c}}",           // без коми дужки лишаються текстом
        "'{A,B}'",                     // лапки скасовують фазу 1
        "~/.bashrc",                   // фаза 2
        "$HOME/*.txt",                 // фази 3 і 5 разом
        "\"$REPORT\"",                 // у лапках поділу немає
        "$REPORT",                     // а тут фаза 4 дає три слова
        "${MISSING:-zapasne znachennia}",
        "${REPORT%% *}",               // обрізання маскою з кінця
        "${#HOME}",                    // довжина значення
        "\"\" tail",                   // порожні лапки — теж аргумент
        "$MISSING kinets",             // незадана змінна зникає зі слова
        "$(date)",                     // відмова: підстановки команд немає
        "'nezakryta lapka",            // відмова: синтаксис
    };
    return lines;
}

}  // namespace

int main(int argc, char** argv)
{
    // Значення з подвійними пробілами всередині — щоб фаза 4 мала що ділити.
    ::setenv("REPORT", "zvit  za  traven", 1);
    ::unsetenv("MISSING");

    const std::span<char* const> args{argv, static_cast<std::size_t>(argc)};

    std::vector<std::string_view> lines;
    if (args.size() > 1) {
        lines.assign(args.begin() + 1, args.end());
    } else {
        lines = demo();
    }

    int failures = 0;
    for (std::string_view line : lines) {
        if (!run(line)) {
            ++failures;
        }
    }

    // У вбудованому наборі дві відмови очікувані — статус це показує.
    return failures > 0 ? 1 : 0;
}
