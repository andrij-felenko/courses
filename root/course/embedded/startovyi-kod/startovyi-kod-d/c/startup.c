#include "mcu_regs.h"
#include "startup.h"

/* Термінальна пастка. Сюди приходять із двох боків: із фатальної помилки
   стартового коду й із повернення main(). Далі по пам'яті лежать чужі
   байти, тож виконувати їх не можна ні в якому разі. */
_Noreturn void startup_trap(void)
{
    if ((COREDEBUG_DHCSR & DHCSR_C_DEBUGEN) != 0U) {
        /* Налагоджувач причеплений — зупиняємо ядро просто тут, щоб у
           вікні відлагоджувача лишились регістри й стек виклику. */
        __asm volatile("bkpt #0");
    }

    /* Без налагоджувача засинаємо: wfi зупиняє тактування ядра до
       наступного переривання або скидання сторожовим таймером. */
    for (;;) {
        __asm volatile("wfi");
    }
}

/* Точка входу. На момент першої інструкції MSP уже завантажений
   апаратно, а більше не готове ніщо: ні змінні, ні тактування. */
void Reset_Handler(void)
{
    /* 1. Своя таблиця векторів. Прошивка за завантажувачем лежить не з
          нуля адресного простору, тож VTOR наводимо на власний масив. */
    if (!startup_relocate_vectors(g_pfnVectors)) {
        startup_trap();
    }

    /* 2. Робочий простір змінних: .data з Flash у RAM, .bss нулями */
    startup_init_memory();

    /* 3. Тактування й затримки Flash. Деградація до HSI не фатальна —
          SystemCoreClock уже містить справжню частоту. */
    (void)SystemInit();

    /* 4. FPU. Якщо прошивку зібрано з -mfloat-abi=hard, а блока в чипі
          немає, перша ж інструкція vldr дасть UsageFault — краще стати
          тут, у передбачуваному місці. */
    const bool fpu_ready = startup_enable_fpu();
#if defined(__ARM_FP)
    if (!fpu_ready) {
        startup_trap();
    }
#else
    (void)fpu_ready;
#endif

    /* 5. Розділяємо винятки: без цього MemManage, BusFault і UsageFault
          ескалюють у спільний HardFault, і причина збою губиться. */
    SCB_SHCSR |= SCB_SHCSR_MEMFAULTENA | SCB_SHCSR_BUSFAULTENA
               | SCB_SHCSR_USGFAULTENA;

    /* 6. Конструктори глобальних об'єктів C++ із .init_array */
    startup_run_init_array();

    /* 7. Середовище готове — віддаємо керування прикладній програмі */
    (void)main();

    /* 8. main() повернувся: далі по пам'яті виконувати нічого */
    startup_trap();
}
