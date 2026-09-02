#include "mcu_regs.h"
#include "startup.h"

/* Номер вектора, який привів нас у пастку: ядро тримає його в IPSR.
   Змінна глобальна й volatile — щоб її було видно в налагоджувачі
   навіть після оптимізації. */
volatile uint32_t g_trapped_vector = 0;

/* Єдиний обробник за замовчуванням. Сюди потрапляє будь-яке переривання,
   яке ввімкнули в NVIC, але забули написати для нього функцію. */
void Default_Handler(void)
{
    uint32_t ipsr = 0;
    __asm volatile("mrs %0, ipsr" : "=r"(ipsr));
    g_trapped_vector = ipsr;

    if ((COREDEBUG_DHCSR & DHCSR_C_DEBUGEN) != 0U) {
        __asm volatile("bkpt #0"); /* зупиняємо ядро для розбору */
    }
    for (;;) {
    }
}

/* Слабкий синонім: символ у таблиці розв'язується в Default_Handler,
   але щойно десь у проєкті з'явиться звичайна функція з такою назвою,
   лінкер віддасть перевагу їй — сильний символ витісняє слабкий. */
#define MCU_WEAK_HANDLER(name) \
    void name(void) __attribute__((weak, alias("Default_Handler")))

MCU_WEAK_HANDLER(NMI_Handler);
MCU_WEAK_HANDLER(HardFault_Handler);
MCU_WEAK_HANDLER(MemManage_Handler);
MCU_WEAK_HANDLER(BusFault_Handler);
MCU_WEAK_HANDLER(UsageFault_Handler);
MCU_WEAK_HANDLER(SVC_Handler);
MCU_WEAK_HANDLER(DebugMon_Handler);
MCU_WEAK_HANDLER(PendSV_Handler);
MCU_WEAK_HANDLER(SysTick_Handler);

/* Те саме для всіх 43 векторів периферії — одним розкриттям переліку */
#define MCU_WEAK_IRQ(name) MCU_WEAK_HANDLER(name);
MCU_IRQ_VECTORS(MCU_WEAK_IRQ)
#undef MCU_WEAK_IRQ
#undef MCU_WEAK_HANDLER
