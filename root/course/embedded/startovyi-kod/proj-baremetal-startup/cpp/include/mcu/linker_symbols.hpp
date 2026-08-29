// linker_symbols.hpp — межі секцій, які видає лінкер, у вигляді std::span.
//
// ⚠ Кожен символ нижче — це АДРЕСА, а не змінна: `_sdata` позначає межу секції,
// байтів під ним не існує. Тому всюди пишеться `&_sdata`. Сирі `extern`
// оголошення сховані тут, а назовні секція виходить діапазоном: у span уже
// вкладено і початок, і довжину, тож переплутати межі різних секцій нічим.

#pragma once

#include <cstddef>
#include <cstdint>
#include <span>

extern "C" {

extern std::uint32_t _sdata;   // початок .data у RAM (VMA)
extern std::uint32_t _edata;   // кінець .data у RAM
extern std::uint32_t _sidata;  // копія початкових значень .data у Flash (LMA)
extern std::uint32_t _sbss;    // початок .bss
extern std::uint32_t _ebss;    // кінець .bss
extern std::uint32_t _end;     // перший вільний байт за глобальними змінними
extern std::uint32_t _estack;  // вершина стека
extern std::uint32_t _Min_Stack_Size;  // резерв під стек, перевірений лінкером

// Таблиці покажчиків на ініціалізатори; заповнює їх компілятор, межі — лінкер.
extern void (*__preinit_array_start[])();
extern void (*__preinit_array_end[])();
extern void (*__init_array_start[])();
extern void (*__init_array_end[])();

}  // extern "C"

namespace mcu::linker {

using Initializer = void (*)();

// Секція .data у RAM — куди копіювати.
inline std::span<std::uint32_t> data_section() noexcept
{
    return {&_sdata, static_cast<std::size_t>(&_edata - &_sdata)};
}

// Її ж образ у Flash — звідки копіювати. Довжина та сама за побудовою.
inline std::span<const std::uint32_t> data_image() noexcept
{
    return {&_sidata, static_cast<std::size_t>(&_edata - &_sdata)};
}

// Секція .bss — що занулити.
inline std::span<std::uint32_t> bss_section() noexcept
{
    return {&_sbss, static_cast<std::size_t>(&_ebss - &_sbss)};
}

inline std::span<Initializer> preinit_array() noexcept
{
    return {__preinit_array_start,
            static_cast<std::size_t>(__preinit_array_end - __preinit_array_start)};
}

inline std::span<Initializer> init_array() noexcept
{
    return {__init_array_start,
            static_cast<std::size_t>(__init_array_end - __init_array_start)};
}

// Нижня межа купи: перший вільний байт за глобальними змінними.
inline std::byte* heap_start() noexcept
{
    return reinterpret_cast<std::byte*>(&_end);
}

// Статична стеля купи: вершина стека мінус резерв, який лінкер уже перевірив
// на етапі збирання. Символ _Min_Stack_Size не має секції, тож його адреса і
// є саме число.
inline std::byte* heap_static_ceiling() noexcept
{
    const auto top = reinterpret_cast<std::uintptr_t>(&_estack);
    const auto reserve = reinterpret_cast<std::uintptr_t>(&_Min_Stack_Size);
    return reinterpret_cast<std::byte*>(top - reserve);
}

inline std::byte* stack_top() noexcept
{
    return reinterpret_cast<std::byte*>(&_estack);
}

// Скільки байтів купи роздано просто зараз. Визначено в memory.cpp — саме там
// живе єдиний об'єкт, що веде облік.
std::size_t heap_used() noexcept;

}  // namespace mcu::linker
