#include "provoke.h"

#include <stdint.h>

#include "trace.h"
#include "stm32f4xx.h"

/*
 * Скрізь volatile і noinline: без них оптимізатор бачить неозначену
 * поведінку, викидає код і стенд перестає падати там, де мусить.
 */

void provoke_null_write(void)
{
    trace_str("provoke: запис за нульовою адресою\r\n");

    volatile uint32_t *const null_ptr = (volatile uint32_t *)0x00000000u;
    *null_ptr = 0xDEADBEEFu; /* на STM32 за адресою 0 лежить дзеркало Flash */
    __DSB();
}

void provoke_unclocked_peripheral(void)
{
    trace_str("provoke: доступ до периферії без тактування\r\n");

    /* USART3, а не USART2: другий канал нам ще потрібен для звіту. */
    RCC->APB1ENR &= ~RCC_APB1ENR_USART3EN;
    __DSB();

    USART3->CR1 = USART_CR1_UE; /* міст APB відповість HRESP = ERROR */
    __DSB();
}

static volatile uint8_t s_packet[8] = { 0xAAu, 0x01u, 0x02u, 0x03u, 0x04u, 0x05u, 0x06u, 0x07u };

void provoke_unaligned(void)
{
    trace_str("provoke: невирівняне читання слова\r\n");

    /* Класика: у кадрі протоколу байт заголовка, а далі 32-бітне поле. */
    const uint32_t          address = (uint32_t)(uintptr_t)&s_packet[1];
    const volatile uint32_t value   = *(const uint32_t *)(uintptr_t)address;

    (void)value; /* спрацює лише при CCR.UNALIGN_TRP = 1 */
}

static __attribute__((noinline)) uint32_t recurse(uint32_t depth)
{
    volatile uint8_t frame_eater[256];

    frame_eater[0] = (uint8_t)depth;
    /* Додавання після виклику не дає компілятору перетворити це на цикл. */
    return frame_eater[0] + recurse(depth + 1u);
}

void provoke_stack_overflow(void)
{
    trace_str("provoke: рекурсія до переповнення стека\r\n");

    volatile uint32_t sink = recurse(0u);
    (void)sink;
}

void provoke_bad_function_pointer(void)
{
    trace_str("provoke: виклик за парною адресою (втрачено біт Thumb)\r\n");

    /* Парна адреса означала б режим ARM, якого в Cortex-M фізично немає. */
    void (*const callback)(void) = (void (*)(void))(uintptr_t)0x08001000u;
    callback();
}

void provoke_divide_by_zero(void)
{
    trace_str("provoke: цілочислове ділення на нуль\r\n");

    volatile int32_t numerator   = 42;
    volatile int32_t denominator = 0;
    volatile int32_t quotient    = numerator / denominator;

    (void)quotient; /* спрацює лише при CCR.DIV_0_TRP = 1 */
}

void provoke_watchdog_hang(void)
{
    trace_str("provoke: зависання без скидання IWDG\r\n");
    trace_flush();

    for (;;) {
        __NOP(); /* сторож добере своє й смикне лінію скидання */
    }
}
