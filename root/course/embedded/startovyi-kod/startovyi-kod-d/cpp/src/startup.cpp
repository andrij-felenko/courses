#include "mcu/fpu.hpp"
#include "mcu/memory_init.hpp"
#include "mcu/registers.hpp"
#include "mcu/startup.hpp"
#include "mcu/vector_table.hpp"
#include "mcu/vtor.hpp"

extern "C" int main();

namespace mcu {

/* Термінальна пастка. Сюди приходять із двох боків: із фатальної помилки
   стартового коду й із повернення main(). Далі по пам'яті лежать чужі
   байти, тож виконувати їх не можна ні в якому разі. */
[[noreturn]] void trap() noexcept
{
    if (scb::dhcsr::all_set(scb::debugger_attached)) {
        /* Налагоджувач причеплений — зупиняємось просто тут, щоб у його
           вікні лишились регістри й стек виклику. */
        breakpoint();
    }

    /* Без налагоджувача засинаємо: wfi зупиняє тактування ядра до
       наступного переривання або скидання сторожовим таймером. */
    for (;;) {
        wait_for_interrupt();
    }
}

} // namespace mcu

/* Точка входу. На момент першої інструкції MSP уже завантажений
   апаратно, а більше не готове ніщо: ні змінні, ні тактування. */
extern "C" void Reset_Handler()
{
    /* 1. Своя таблиця векторів: прошивка за завантажувачем лежить не з
          нуля адресного простору. */
    if (!mcu::relocate_vector_table(&g_vector_table)) {
        mcu::trap();
    }

    /* 2. Робочий простір змінних: .data з Flash у RAM, .bss нулями */
    mcu::init_memory();

    /* 3. Тактування й затримки Flash. Деградація до HSI не фатальна —
          core_clock_hz уже містить справжню частоту, і прикладний код
          побачить, що працює повільніше. */
    static_cast<void>(mcu::configure_clock());

    /* 4. FPU. Якщо прошивку зібрано з -mfloat-abi=hard, а блока в чипі
          немає, перша ж інструкція vldr дасть UsageFault — краще стати
          тут, у передбачуваному місці. */
    const auto fpu = mcu::enable_fpu();
#if defined(__ARM_FP)
    if (!fpu) {
        mcu::trap();
    }
#else
    static_cast<void>(fpu);
#endif

    /* 5. Розділяємо винятки: без цього MemManage, BusFault і UsageFault
          ескалюють у спільний HardFault, і причина збою губиться. */
    mcu::scb::shcsr::set(mcu::scb::memfault_enable | mcu::scb::busfault_enable
                         | mcu::scb::usgfault_enable);

    /* 6. Конструктори глобальних об'єктів із .init_array */
    mcu::run_init_array();

    /* 7. Середовище готове — керування йде прикладній програмі */
    static_cast<void>(main());

    /* 8. main() повернувся: далі по пам'яті виконувати нічого */
    mcu::trap();
}
