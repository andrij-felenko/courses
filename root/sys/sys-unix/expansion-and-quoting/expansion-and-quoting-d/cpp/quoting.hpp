// quoting.hpp — примітиви розбору лапок і поділ сирого рядка на слова.
//
// Лапки на цьому кроці лишаються на місці: фаза 1 (дужки) мусить їх
// бачити, бо саме вони її й скасовують. Знімає лапки фаза 6, і робить
// це marked_word.cpp — разом із позначками, що з чого взялося.
#pragma once

#include <cstddef>
#include <string>
#include <string_view>
#include <vector>

namespace shexp {

// Індекс першого байта ПІСЛЯ лапки чи екрана, що починається на line[i];
// для звичайного байта — просто i + 1. Незакрита лапка тягнеться до кінця.
[[nodiscard]] std::size_t skip_quoted(std::string_view line, std::size_t i);

// Поділ рядка на сирі слова за незахищеними пробілами.
[[nodiscard]] std::vector<std::string> split_words(std::string_view line);

}  // namespace shexp
