// expansion.hpp — розгортання рядка правилами оболонки, без підстановки команд.
//
// Той самий wordexp(3), але контракт інший: помилка приходить винятком,
// а пам'ять вектора слів звільняє RAII, тож забути wordfree(3) неможливо.
#pragma once

#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

namespace shexp {

// Відмова розгортання. Несе код WRDE_* поруч із поясненням українською.
class expand_error : public std::runtime_error {
public:
    expand_error(int status, const std::string& message)
        : std::runtime_error(message), status_{status} {}

    [[nodiscard]] int status() const noexcept { return status_; }

private:
    int status_;
};

// Розгортає рядок із прапорами WRDE_NOCMD | WRDE_UNDEF.
// Повертає готовий вектор слів — саме те, що лягло б в argv[].
// Кидає expand_error, якщо wordexp(3) відмовив.
[[nodiscard]] std::vector<std::string> expand(std::string_view line);

}  // namespace shexp
