// Правило зіставлення дня: поля «день місяця» (DOM) і «день тижня» (DOW)
// зв'язані окремим правилом POSIX.1, а не звичайним «І».
#pragma once

#include <bitset>
#include <ctime>
#include <string_view>

namespace minicron {

struct DayFields {
    std::bitset<32> dom;        // біти 1..31
    std::bitset<7>  dow;        // біти 0..6, неділя — 0
    // ФОРМА полів: саме вона, а не вміст масок, обирає правило.
    bool dom_star = false;
    bool dow_star = false;

    [[nodiscard]] bool matches(const std::tm& now) const noexcept;
    [[nodiscard]] std::string_view rule() const noexcept;
};

}  // namespace minicron
