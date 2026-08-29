/* clock_gate.hpp — крок 1 методики: подача тактового сигналу на блок.
 *
 * До запису біта тактування периферія мовчить, а звернення до її регістрів
 * не отримує підтвердження на шині й перетворюється на BusFault. Обхід
 * еррати «Delay after an RCC peripheral clock enabling» живе тут, в одному
 * місці, — решта модулів вмикає тактування лише цими функціями.
 */
#pragma once

#include <cstdint>

#include "hw/registers.hpp"
#include "hw/silicon.hpp"

namespace hw::clocks {

namespace detail {

inline void enable_and_settle(volatile std::uint32_t& enr, std::uint32_t mask) noexcept
{
    enr |= mask;

    /* Офіційний обхід: прочитати той самий регістр назад. Читання по шині
     * не завершиться, доки не осяде попередній запис, — потрібна затримка
     * виникає сама, без калібрування циклів. На виправлених ревізіях гілка
     * не виконується, і старт не коштує зайвих тактів. */
    if (silicon::affected(silicon::Erratum::rcc_clock_enable_delay)) {
        [[maybe_unused]] const volatile std::uint32_t readback = enr;
    }
}

} // namespace detail

inline void enable_ahb1(std::uint32_t mask) noexcept
{
    detail::enable_and_settle(rcc().ahb1enr, mask);
}

inline void enable_apb1(std::uint32_t mask) noexcept
{
    detail::enable_and_settle(rcc().apb1enr, mask);
}

inline void disable_apb1(std::uint32_t mask) noexcept
{
    rcc().apb1enr &= ~mask;
}

/* Скидання — імпульс, а не стан: біт треба виставити й зняти, лишивши між
 * фронтами час на те, щоб блок побачив активний рівень. */
inline void reset_apb1(std::uint32_t mask) noexcept
{
    rcc().apb1rstr |= mask;
    [[maybe_unused]] const volatile std::uint32_t readback = rcc().apb1rstr;
    rcc().apb1rstr &= ~mask;
}

} // namespace hw::clocks
