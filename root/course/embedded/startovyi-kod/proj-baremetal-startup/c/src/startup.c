/* startup.c — векторна таблиця й точка входу Reset_Handler.

   Таблиця векторів, Default_Handler і сам Reset_Handler живуть в одному модулі
   навмисно: слабкі псевдоніми обробників мусять посилатися на ціль із ТОГО
   САМОГО модуля трансляції, інакше лінкер не зв'яже alias.

   ⚠ Код цього файла виконується ДО того, як RAM набула коректного стану.
   Тому Reset_Handler і все, що він кличе до кроку 3.3, не має права читати
   глобальні змінні: .data ще лежить у Flash, а .bss заповнена сміттям після
   подачі живлення. Дозволено лише локальні змінні на стеку й символи лінкера. */

#include <stddef.h>
#include <stdint.h>

#include "cortex_m.h"
#include "startup.h"

int main(void);

/* ── 1. Обробники системних винятків ───────────────────────────────────────
   Кожен — слабкий псевдонім Default_Handler. Щойно прошивка визначить звичайну
   функцію з таким самим іменем, лінкер побачить сильний символ і підставить
   у таблицю адресу користувацької версії — без жодної правки тут. */

void NMI_Handler(void)        __attribute__((weak, alias("Default_Handler")));
void HardFault_Handler(void)  __attribute__((weak, alias("Default_Handler")));
void MemManage_Handler(void)  __attribute__((weak, alias("Default_Handler")));
void BusFault_Handler(void)   __attribute__((weak, alias("Default_Handler")));
void UsageFault_Handler(void) __attribute__((weak, alias("Default_Handler")));
void SVC_Handler(void)        __attribute__((weak, alias("Default_Handler")));
void DebugMon_Handler(void)   __attribute__((weak, alias("Default_Handler")));
void PendSV_Handler(void)     __attribute__((weak, alias("Default_Handler")));
void SysTick_Handler(void)    __attribute__((weak, alias("Default_Handler")));

/* Векторна таблиця в секції .isr_vector. Атрибут used забороняє компілятору
   викинути масив, на який ніхто не посилається з коду, а KEEP у скрипті
   лінкера — вирізати секцію при --gc-sections.

   Перші 16 записів визначені архітектурою. Вектори периферії конкретного чипа
   (WWDG, TIM2, USART1 …) дописуються нижче за тим самим зразком: слабкий
   псевдонім у списку вище плюс рядок у масиві. */
__attribute__((section(".isr_vector"), used))
void (*const g_pfnVectors[])(void) = {
    (void (*)(void))(&_estack), /* 0x00: початкова вершина стека MSP */
    Reset_Handler,              /* 0x04: точка входу після скидання  */
    NMI_Handler,                /* 0x08: немасковане переривання     */
    HardFault_Handler,          /* 0x0C: фатальний збій              */
    MemManage_Handler,          /* 0x10: порушення захисту MPU       */
    BusFault_Handler,           /* 0x14: помилка шини                */
    UsageFault_Handler,         /* 0x18: невірна інструкція, ділення на 0 */
    0, 0, 0, 0,                 /* 0x1C..0x28: зарезервовано ARM     */
    SVC_Handler,                /* 0x2C: системний виклик            */
    DebugMon_Handler,           /* 0x30: монітор налагодження        */
    0,                          /* 0x34: зарезервовано ARM           */
    PendSV_Handler,             /* 0x38: відкладений виклик RTOS     */
    SysTick_Handler,            /* 0x3C: системний таймер            */
};

/* ── 2. Розгортання середовища ─────────────────────────────────────────────── */

/* Увімкнення співпроцесора з рухомою комою (Cortex-M4F / M7 / M33).
   Після скидання CP10 і CP11 апаратно вимкнені задля енергозбереження: перша ж
   інструкція vldr при вимкненому FPU дає UsageFault з ознакою NOCP. */
static void enable_fpu(void)
{
    CM_REG32(SCB_CPACR) |= SCB_CPACR_CP10_CP11_FULL;
    /* dsb доводить запис у CPACR до кінця, isb очищує конвеєр: наступні
       інструкції з рухомою комою декодуються вже увімкненим співпроцесором. */
    cm_dsb();
    cm_isb();
}

/* Обхід однієї таблиці покажчиків на функції-ініціалізатори. */
static void run_init_table(void (**begin)(void), void (**end)(void))
{
    for (void (**entry)(void) = begin; entry != end; ++entry) {
        if (*entry != NULL) {
            (*entry)();
        }
    }
}

/* Рантайм C++: конструктори глобальних об'єктів і функції з атрибутом
   constructor. .preinit_array виконується першим — так вимагає стандарт. */
static void run_static_constructors(void)
{
    run_init_table(__preinit_array_start, __preinit_array_end);
    run_init_table(__init_array_start, __init_array_end);
}

/* ── 3. Точка входу після апаратного скидання ───────────────────────────────

   Атрибут no-tree-loop-distribute-patterns вимикає рівно одну оптимізацію GCC:
   розпізнавання циклів копіювання та обнулення й заміну їх на виклики memcpy і
   memset. Доки .data і .bss не набули коректного стану, такий виклик — стрибок
   у бібліотеку, чиї власні дані ще не існують. Прапорець -fno-builtin у збірці
   робить те саме глобально; атрибут страхує модуль незалежно від прапорців. */
__attribute__((used, noreturn, optimize("no-tree-loop-distribute-patterns")))
void Reset_Handler(void)
{
    /* 3.1 Копіювання початкових значень .data з Flash (LMA) у RAM (VMA). */
    uint32_t *src = &_sidata;
    for (uint32_t *dst = &_sdata; dst < &_edata; ++dst, ++src) {
        *dst = *src;
    }

    /* 3.2 Занулення .bss: у прошивці секція займає 0 байтів, тож заповнити її
           нулями — обов'язок стартового коду, а не лінкера. */
    for (uint32_t *bss = &_sbss; bss < &_ebss; ++bss) {
        *bss = 0;
    }

    /* Від цього рядка глобальні змінні мають коректні значення. */

    /* 3.3 Ядро: співпроцесор, векторна таблиця, дозволені винятки. */
    enable_fpu();
    SystemInit();

    /* 3.4 Конструктори глобальних об'єктів. */
    run_static_constructors();

    /* 3.5 Передача керування прикладній програмі. */
    (void)main();

    /* 3.6 Термінальна пастка. Повертатися main() нема куди: операційної системи
           не існує, а за кінцем стартового коду лежать чужі байти. wfi спиняє
           тактування ядра до наступного переривання — пастка не гріє чіп. */
    for (;;) {
        cm_wfi();
    }
}

/* ── 4. Вектор, який прошивка не перевизначила ─────────────────────────────
   Порожній вічний цикл приховав би причину: під налагоджувачем видно лише
   «десь крутиться». bkpt спиняє ядро саме тут, а номер винятку, що спрацював,
   лишається в ICSR — під GDB його читає команда з tools/startup-check.gdb. */
__attribute__((noreturn))
void Default_Handler(void)
{
    cm_bkpt();
    for (;;) {
        cm_wfi();
    }
}
