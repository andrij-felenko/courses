#pragma once

#include <bit>
#include <cstdint>

#include "mcu/registers.hpp"
#include "mcu/startup.hpp"
#include "mcu/vector_table.hpp"

namespace mcu {

/* Перенесення таблиці векторів. Завантажувач лишає основній прошивці
   зсув у Flash (скажімо, 0x08010000), а RTOS часом тримає таблицю в
   RAM, щоб міняти обробники на льоту. */
[[nodiscard]] inline startup_result
relocate_vector_table(const void* table_base) noexcept
{
    const auto base = std::bit_cast<std::uintptr_t>(table_base);

    /* VTOR просто ігнорує молодші біти адреси: незарівняна таблиця не
       дасть помилки — вона мовчки поїде на кілька сотень байтів нижче,
       і перше ж переривання піде за випадковою адресою. */
    if ((base % vector_table_align) != 0U) {
        return std::unexpected{startup_error::vector_table_misaligned};
    }

    scb::vtor::write(static_cast<std::uint32_t>(base));
    dsb(); /* запис мусить дійти до шини… */
    isb(); /* …а конвеєр — забути старі адреси */

    return {};
}

} // namespace mcu
