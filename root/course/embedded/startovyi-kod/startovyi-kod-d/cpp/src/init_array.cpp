#include <cstddef>
#include <ranges>
#include <span>

#include "mcu/startup.hpp"

namespace {
using init_function = void (*)();
}

/* Межі таблиць покажчиків розставляє лінкер. У .preinit_array складають
   ініціалізацію, яка мусить відпрацювати ДО конструкторів, у
   .init_array — самі конструктори глобальних об'єктів. */
extern "C" {
extern init_function __preinit_array_start[];
extern init_function __preinit_array_end[];
extern init_function __init_array_start[];
extern init_function __init_array_end[];
}

namespace mcu {
namespace {

[[nodiscard]] std::span<init_function> table_between(init_function* begin,
                                                     init_function* end) noexcept
{
    return {begin, static_cast<std::size_t>(end - begin)};
}

void invoke_all(std::span<init_function> table) noexcept
{
    /* Порожній запис лишає лінкер, коли викидає невикористаний об'єктний
       файл: викликати нуль означало б стрибок у нікуди. */
    for (const init_function fn :
         table | std::views::filter([](init_function f) { return f != nullptr; })) {
        fn();
    }
}

} // namespace

void run_init_array() noexcept
{
    invoke_all(table_between(__preinit_array_start, __preinit_array_end));
    invoke_all(table_between(__init_array_start, __init_array_end));
}

} // namespace mcu
