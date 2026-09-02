// fields.hpp — фаза 4 конвеєра: поділ на слова за IFS.
//
// Ділиться ЛИШЕ те, що прийшло з підстановки і не було в лапках. Саме
// тому маска походження з marked_word дожила до цього місця: буквальний
// пробіл, набраний користувачем, слово вже поділив на етапі лексики,
// а пробіл із значення змінної ділить його аж тут.
#pragma once

#include <string_view>
#include <vector>

#include "marked_word.hpp"

namespace shexp {

[[nodiscard]] std::vector<marked_word> split_fields(const marked_word& w,
                                                    std::string_view ifs);

}  // namespace shexp
