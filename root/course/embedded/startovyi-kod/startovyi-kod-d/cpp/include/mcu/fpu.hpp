#pragma once

#include "mcu/registers.hpp"
#include "mcu/startup.hpp"

namespace mcu {

/* Увімкнення співпроцесора з рухомою комою. Після скидання CP10 і CP11
   вимкнені задля економії струму, і перша ж інструкція vldr дала б
   UsageFault із прапорцем NOCP у регістрі UFSR. */
[[nodiscard]] inline startup_result enable_fpu() noexcept
{
    scb::cpacr::set(scb::fpu_full_access); /* 0b11 у кожне поле = повний доступ */
    dsb();
    isb();

    /* На ядрі без FPU ці біти читаються нулями: так прошивка дізнається,
       що її зібрано не для цього чипа. */
    if (!scb::cpacr::all_set(scb::fpu_full_access)) {
        return std::unexpected{startup_error::fpu_absent};
    }
    return {};
}

} // namespace mcu
