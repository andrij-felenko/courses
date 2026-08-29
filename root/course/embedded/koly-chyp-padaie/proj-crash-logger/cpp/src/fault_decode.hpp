// Розшифровка дампу в текст: заради цього все й затівалося — щоб причина була
// видна з першого погляду в терміналі, а не після години з даташитом.
#pragma once

#include <cstdint>
#include <string_view>

#include "crash_record.hpp"

namespace crash {

// Пара «біт — що він означає». Таблиці нижче constexpr, тож увесь опис
// прапорців лежить у флеші й не займає жодного байта RAM.
struct FlagName {
    std::uint32_t mask;
    std::string_view name;
};

// rcc_csr — знімок RCC->CSR, зроблений на початку main() до скидання RMVF.
void print_reset_cause(std::uint32_t rcc_csr);

void print(const Record& record);

} // namespace crash
