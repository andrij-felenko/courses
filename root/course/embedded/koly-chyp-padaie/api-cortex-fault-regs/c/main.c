/* main.c — порядок дій на старті: спершу дізнатися, ЧОМУ ми тут,
 * потім налаштувати діагностику, і лише потім робити щось корисне.
 */
#include "diag_out.h"
#include "fault_diag.h"
#include "reset_cause.h"

#include "stm32f4xx.h"

/* Який саме збій провокуємо для демонстрації розбору. */
enum demo_fault {
    DEMO_DIV_BY_ZERO,
    DEMO_UNALIGNED,
    DEMO_BAD_ADDRESS,
    DEMO_UNDEFINED_INSTRUCTION,
};

static const enum demo_fault k_demo = DEMO_BAD_ADDRESS;

static void provoke(enum demo_fault kind)
{
    switch (kind) {
    case DEMO_DIV_BY_ZERO: {
        /* volatile, щоб компілятор не порахував це сам і не викинув ділення. */
        volatile int divisor = 0;
        volatile int result = 42 / divisor;
        (void)result;
        break;                       /* → UsageFault: DIVBYZERO */
    }
    case DEMO_UNALIGNED: {
        /* Адреса в RAM, зсунута на байт: при UNALIGN_TRP=1 звичайний STR
         * теж стає збоєм. */
        volatile uint32_t *p = (volatile uint32_t *)(SRAM_BASE + 1u);
        *p = 0xDEADBEEFu;
        break;                       /* → UsageFault: UNALIGNED */
    }
    case DEMO_BAD_ADDRESS: {
        /* Дірка в карті адрес: читання не знаходить ані пам'яті, ані
         * периферії, і шина відповідає помилкою. */
        volatile uint32_t v = *(volatile uint32_t *)0xCC000000u;
        (void)v;
        break;                       /* → BusFault: PRECISERR + BFARVALID */
    }
    case DEMO_UNDEFINED_INSTRUCTION:
        /* UDF #0 — навмисно недійсний опкод. */
        __asm volatile(".short 0xDE00");
        break;                       /* → UsageFault: UNDEFINSTR */
    }
}

int main(void)
{
    /* Крок 1. Причину скидання читаємо ПЕРШОЮ дією: прапорці липкі, і поки
     * ми їх не стерли, вони описують попередній прогін, а не цей. */
    const uint32_t csr = reset_cause_read();
    reset_cause_clear();

    diag_puts("\n--- старт прошивки ---\n");
    reset_cause_report(csr);

    /* Крок 2. Діагностичне середовище — до першого власного коду, інакше
     * ранній збій прийде як безіменний HardFault. */
    fault_diag_init();

    /* Крок 3. Демонстрація: валимо ядро наперед відомим способом і дивимось,
     * що саме покаже розбір регістрів. */
    diag_puts("Провокуємо збій...\n");
    provoke(k_demo);

    /* Сюди керування не повертається: provoke() гарантовано впаде,
     * а fault_report_entry() зупиняє або перезавантажує ядро. */
    diag_puts("ПОМИЛКА: збою не сталося — перевір, чи ввімкнено пастки в CCR\n");
    for (;;) {
    }
}
