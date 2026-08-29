#include <stdint.h>

#include "fault.h"
#include "provoke.h"
#include "reset_cause.h"
#include "trace.h"
#include "stm32f4xx.h"

/* Ключі доступу до регістрів IWDG — задані апаратурою. */
#define IWDG_KEY_FEED   0x0000AAAAu
#define IWDG_KEY_WRITE  0x00005555u
#define IWDG_KEY_START  0x0000CCCCu

/* LSI ~32 кГц; дільник 64 дає 500 тактів на секунду, перезавантаження 1000 ≈ 2 с. */
static void watchdog_start(void)
{
    IWDG->KR  = IWDG_KEY_WRITE;
    IWDG->PR  = 4u;
    IWDG->RLR = 1000u;
    while (IWDG->SR != 0u) {
        /* чекаємо, доки значення перепишуться в домен LSI */
    }
    IWDG->KR = IWDG_KEY_FEED;
    IWDG->KR = IWDG_KEY_START;
}

static void watchdog_feed(void)
{
    IWDG->KR = IWDG_KEY_FEED;
}

static void print_menu(void)
{
    trace_str("\r\nстенд аварій (натисни цифру):\r\n"
              "  1 запис за NULL\r\n"
              "  2 периферія без тактування\r\n"
              "  3 невирівняне читання\r\n"
              "  4 переповнення стека\r\n"
              "  5 виклик за парною адресою\r\n"
              "  6 ділення на нуль\r\n"
              "  7 зависання під сторожем\r\n");
}

int main(void)
{
    /*
     * Порядок важливий. Спершу UART — інакше звіт нікуди друкувати.
     * Далі прапорці скидання, поки їх ніхто не стер. І лише потім усе решта.
     */
    trace_init();

    const uint32_t cause = reset_cause_capture();

    trace_str("\r\n=== старт прошивки ===\r\n");
    reset_cause_print(cause);

    if (reset_cause_is_crash(cause)) {
        trace_str("попередній запуск завершився крахом\r\n");
    }

    fault_enable_all();
    watchdog_start();
    print_menu();

    for (;;) {
        watchdog_feed();

        switch (trace_getc()) {
        case '1': provoke_null_write(); break;
        case '2': provoke_unclocked_peripheral(); break;
        case '3': provoke_unaligned(); break;
        case '4': provoke_stack_overflow(); break;
        case '5': provoke_bad_function_pointer(); break;
        case '6': provoke_divide_by_zero(); break;
        case '7': provoke_watchdog_hang(); break;
        case -1: break; /* байта немає — звичайний холостий оберт */
        default:
            print_menu();
            break;
        }
    }
}
