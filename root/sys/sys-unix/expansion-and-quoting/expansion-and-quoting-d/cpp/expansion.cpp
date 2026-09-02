#include "expansion.hpp"

#include <span>

#include <wordexp.h>

namespace shexp {
namespace {

std::string describe(int status)
{
    switch (status) {
    case WRDE_BADCHAR:
        return "заборонений символ поза лапками: | & ; < > ( ) { } новий рядок";
    case WRDE_BADVAL:
        return "звертання до невизначеної змінної (діє WRDE_UNDEF)";
    case WRDE_CMDSUB:
        return "спроба підстановки команди заблокована прапором WRDE_NOCMD";
    case WRDE_NOSPACE:
        return "бракує пам'яті для вектора слів";
    case WRDE_SYNTAX:
        return "синтаксична помилка: незакриті лапки або обірваний вираз";
    default:
        return "невідомий код помилки wordexp(3)";
    }
}

// Власник результату wordexp(3): захоплює в конструкторі, віддає в деструкторі.
class wordexp_guard {
public:
    explicit wordexp_guard(const char* line)
    {
        const int status = ::wordexp(line, &we_, WRDE_NOCMD | WRDE_UNDEF);
        if (status != 0) {
            // Після невдачі структуру звільняти не можна й не треба:
            // об'єкт не збудовано, деструктор не викличеться.
            throw expand_error{status, describe(status)};
        }
        held_ = true;
    }

    ~wordexp_guard()
    {
        if (held_) {
            ::wordfree(&we_);
        }
    }

    wordexp_guard(const wordexp_guard&) = delete;
    wordexp_guard& operator=(const wordexp_guard&) = delete;

    [[nodiscard]] std::span<char* const> words() const noexcept
    {
        return {we_.we_wordv, we_.we_wordc};
    }

private:
    wordexp_t we_{};
    bool held_{false};
};

}  // namespace

std::vector<std::string> expand(std::string_view line)
{
    // wordexp(3) вимагає рядка, завершеного нулем, а string_view його не гарантує.
    const std::string text{line};

    const wordexp_guard guard{text.c_str()};
    const std::span<char* const> words = guard.words();

    // Копіюємо, поки guard живий: після нього покажчики недійсні.
    return std::vector<std::string>{words.begin(), words.end()};
}

}  // namespace shexp
