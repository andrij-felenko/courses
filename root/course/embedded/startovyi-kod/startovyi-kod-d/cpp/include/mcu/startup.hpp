#pragma once

#include <cstdint>
#include <expected>

namespace mcu {

/* Чого стартовий код може не зуміти. Винятків тут іще немає — рантайм
   не піднятий, — тож помилку несе значення, що повертається. */
enum class startup_error {
    vector_table_misaligned, /* VTOR мовчки відкине молодші біти адреси */
    fpu_absent,              /* прошивку зібрано з апаратною комою не для цього ядра */
    hse_not_ready,           /* зовнішній кварц не завівся */
    pll_not_locked,          /* PLL не захопився */
    clock_switch_failed,     /* ядро не перемкнулося на PLL */
};

using startup_result = std::expected<void, startup_error>;

/* Справжня частота ядра після configure_clock(). Живе в .data, тож до
   розгортання пам'яті читати її не можна. */
inline std::uint32_t core_clock_hz = 16'000'000U;

/* Термінальна пастка: фатальна помилка старту або повернення з main() */
[[noreturn]] void trap() noexcept;

/* Тактування, затримки Flash, дільники шин */
[[nodiscard]] startup_result configure_clock() noexcept;

/* Обхід .preinit_array і .init_array — конструктори глобальних об'єктів */
void run_init_array() noexcept;

} // namespace mcu
