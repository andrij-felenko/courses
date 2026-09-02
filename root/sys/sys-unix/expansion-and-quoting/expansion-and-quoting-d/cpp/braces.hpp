// braces.hpp — фаза 1 конвеєра: розгортання фігурних дужок.
//
// wordexp(3) її не виконує: дужки не входять у POSIX, це розширення
// Bash, Zsh і Ksh. Списки {a,b}, довільне вкладення {a,b{1,2}},
// діапазони {1..9..2}, {a..e} і {01..05} з шириною поля.
#pragma once

#include <string>
#include <string_view>
#include <vector>

namespace shexp {

// Кидає expand_error, якщо один запис породжує понад чотири тисячі слів.
[[nodiscard]] std::vector<std::string> expand_braces(std::string_view word);

}  // namespace shexp
