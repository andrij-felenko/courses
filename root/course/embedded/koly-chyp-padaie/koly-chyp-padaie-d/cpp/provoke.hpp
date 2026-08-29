#pragma once

#include <span>
#include <string_view>

namespace provoke {

// Навчальний стенд: кожна аварія має відомий наперед відбиток у регістрах,
// тож студент натискає клавішу й звіряє звіт обробника з теорією.
struct Case {
    char             key;
    std::string_view label;
    void (*run)();
};

void null_write();           // BFSR.PRECISERR, BFAR = 0x00000000
void unclocked_peripheral(); // BFSR.IMPRECISERR (або PRECISERR при DISDEFWBUF)
void unaligned_load();       // UFSR.UNALIGNED
void stack_overflow();       // UFSR.UNDEFINSTR / INVSTATE або MMFSR.MSTKERR
void bad_function_pointer(); // UFSR.INVSTATE
void divide_by_zero();       // UFSR.DIVBYZERO
void watchdog_hang();        // без скидання IWDG: RCC->CSR.IWDGRSTF

[[nodiscard]] std::span<const Case> catalogue() noexcept;

// Виконує сценарій із таким ключем; false — такого ключа в каталозі немає.
bool run(char key);

} // namespace provoke
