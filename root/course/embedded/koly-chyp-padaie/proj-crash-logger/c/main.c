// Аварійний реєстратор у зборі: після кожного скидання прошивка спершу каже,
// ЧОМУ вона перезапустилася, і лише потім береться до роботи.
#include <stdint.h>

#include "crash_dump.h"
#include "crash_guard.h"
#include "fault_handler.h"
#include "fault_report.h"
#include "stm32f4xx.h"
#include "uart_sync.h"

#define SYSCLK_HZ 168000000u
#define PCLK2_HZ 84000000u

#define RST_IWDG (1u << 29)
#define RST_WWDG (1u << 30)

static volatile uint32_t g_uptime_ms;

void SysTick_Handler(void)
{
    g_uptime_ms++;
}

// Чотири способи зламати чип — кожен вмикає свій біт CFSR, і звіт після
// перезапуску показує, який саме.
static void provoke_bus_fault(void)
{
    volatile uint32_t *bad = (volatile uint32_t *)0xCCCCCCCCu;
    (void)*bad;
}

static void provoke_div_by_zero(void)
{
    volatile int zero = 0;
    volatile int result = 42 / zero;
    (void)result;
}

static void provoke_invalid_state(void)
{
    // Адреса без біта Thumb: ядро відмовиться туди переходити (INVSTATE).
    void (*bad_call)(void) = (void (*)(void))0x20000000u;
    bad_call();
}

static void provoke_unaligned(void)
{
    volatile uint32_t *odd = (volatile uint32_t *)0x20000002u;
    *odd = 1u;
}

static void print_menu(void)
{
    (void)uart_sync_write(
        "[menu] b - bus fault, d - ділення на нуль, i - INVSTATE, u - невирівняний доступ\r\n");
}

int main(void)
{
    uart_sync_init(PCLK2_HZ, 115200u);

    // Вмикаємо окремі вектори якнайраніше: аварія під час ініціалізації
    // периферії — найчастіший випадок, і саме її найважче зловити.
    fault_handler_init();

    // Знімок причини скидання робимо ДО RMVF: прапорці накопичуються, і без
    // очищення наступний старт покаже суміш із двох перезапусків.
    const uint32_t reset_flags = RCC->CSR;
    RCC->CSR |= RCC_CSR_RMVF;

    (void)uart_sync_write("\r\n===== старт прошивки =====\r\n");
    fault_report_reset_cause(reset_flags);

    static crash_dump_t dump; // статичний: у main теж не роздуваємо стек
    if (crash_dump_take(&dump)) {
        fault_report_dump(&dump);
    } else if ((reset_flags & (RST_IWDG | RST_WWDG)) != 0u) {
        // Сторожовий таймер зупинив зависання — дампу немає, бо HardFault не
        // спрацьовував. Але перезапуск усе одно аварійний, і його треба
        // порахувати, інакше зависання проскочить повз захист від циклу.
        (void)crash_dump_bump_counter();
        (void)uart_sync_write("[crash] скидання сторожовим таймером, дампу немає\r\n");
    } else {
        (void)uart_sync_write("[crash] дампу немає — минулий сеанс завершився штатно\r\n");
    }

    if (crash_guard_decide() == BOOT_SAFE) {
        crash_guard_safe_mode(); // не повертається
    }

    SysTick_Config(SYSCLK_HZ / 1000u);
    print_menu();

    for (;;) {
        crash_guard_mark_healthy(g_uptime_ms);

        char cmd = 0;
        if (!uart_sync_read(&cmd)) {
            continue;
        }
        switch (cmd) {
        case 'b':
            provoke_bus_fault();
            break;
        case 'd':
            provoke_div_by_zero();
            break;
        case 'i':
            provoke_invalid_state();
            break;
        case 'u':
            provoke_unaligned();
            break;
        default:
            print_menu();
            break;
        }
    }
}
