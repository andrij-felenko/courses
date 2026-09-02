// builtins.hpp — самі функції, які модуль додає до AWK.
//
// Сигнатура диктується <gawkapi.h> і мінятися не може: кількість фактичних
// аргументів, місце під результат (його ж і повертаємо) та дескриптор
// функції, звідки беруть .data.
#pragma once

#include <gawkapi.h>

namespace fast_tools {

// Обидві noexcept НЕ для оптимізації: виняток, кинутий крізь межу C-виклику,
// розкручував би стек через кадри інтерпретатора — тобто негайний крах.
// noexcept перетворює цю ваду на чесний std::terminate у своєму ж кадрі.

// monotonic_time_ns() -> число. Монотонний годинник ОС у наносекундах.
awk_value_t *monotonic_time_ns(int nargs, awk_value_t *result,
                               struct awk_ext_func *finfo) noexcept;

// fnv1a_64(str) -> рядок "0x................".
awk_value_t *fnv1a_64_of_string(int nargs, awk_value_t *result,
                                struct awk_ext_func *finfo) noexcept;

} // namespace fast_tools
