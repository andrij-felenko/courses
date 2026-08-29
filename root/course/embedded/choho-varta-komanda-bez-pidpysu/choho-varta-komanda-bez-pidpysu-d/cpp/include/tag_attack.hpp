#pragma once

#include <cstdint>
#include <expected>

#include "constant_time.hpp"
#include "timing_oracle.hpp"

namespace ct {

/// Тег зібрано, і приймач його прийняв.
struct Recovered {
    Tag tag;
    std::uint64_t queries;
};

/// Приймач не піддався: лишився найкращий здогад нападника.
struct Rejected {
    Tag best_guess;
    std::uint64_t queries;
};

/// Підбирає тег байт за байтом за часом відповіді приймача.
///
/// Ні ключа, ні алгоритму MAC нападник не знає. Він спирається лише на те,
/// що з вгаданим байтом порівняння доходить на крок далі — і цим замінює
/// перебір 2^256 на 32 незалежні перебори по 256 варіантів.
///
/// Замість -1 з errno повертаємо std::expected: невдача несе із собою те,
/// що з неї варто прочитати, — здогад і ціну спроби.
[[nodiscard]] std::expected<Recovered, Rejected> recover_tag(TimingOracle& oracle);

}  // namespace ct
