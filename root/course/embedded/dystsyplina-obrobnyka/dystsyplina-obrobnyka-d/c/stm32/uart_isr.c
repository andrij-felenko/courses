#include "uart_isr.h"

#include "FreeRTOS.h"
#include "task.h"

#include "stm32f4xx.h"
#include "stm32f4xx_ll_usart.h"

#include "../spsc_ring.h"
#include "frame_parser.h"
#include "timer_isr.h"

#define UART_TASK_STACK_WORDS 384u

static spsc_ring_buffer_t s_rx_ring;
static uart_isr_stats_t s_stats;
static TaskHandle_t s_consumer = NULL;

static StaticTask_t s_task_tcb;
static StackType_t s_task_stack[UART_TASK_STACK_WORDS];

static frame_parser_t s_parser;

/* ---------------------------------------------------------------------------
 * ВЕРХНЯ ПОЛОВИНА. Усе, що тут написано, виконується з пріоритетом, вищим
 * за будь-який код застосунку. Тому тут немає ні циклів невизначеної
 * довжини, ні викликів, чия тривалість залежить від даних.
 * ------------------------------------------------------------------------ */
void USART1_IRQHandler(void)
{
    /* Лічильник тактів ядра (DWT) — єдиний чесний спосіб дізнатися, скільки
     * ISR справді триває. Осцилограф на ніжці показує те саме, але його
     * не візьмеш у поле. */
    const uint32_t entry_cycles = DWT->CYCCNT;

    BaseType_t higher_priority_woken = pdFALSE;
    bool signal_consumer = false;

    /* Переповнення приймача розбираємо ПЕРШИМ. Поки ORE висить, RXNE на F4
     * більше не зводиться, і мовчазне ігнорування прапорця перетворює
     * обробник на нескінченне холосте спрацювання. */
    if (LL_USART_IsActiveFlag_ORE(USART1)) {
        LL_USART_ClearFlag_ORE(USART1); /* послідовність «читання SR, потім DR» */
        s_stats.hw_overruns++;
        signal_consumer = true;
    }

    /* Цикл обмежений залізом: RXNE зводиться рівно одним прийнятим байтом,
     * а приймальний регістр у F4 один. Це не busy-wait — вихід тут
     * гарантований і без зовнішньої апаратури. */
    while (LL_USART_IsActiveFlag_RXNE(USART1) && LL_USART_IsEnabledIT_RXNE(USART1)) {
        /* Читання DR саме по собі знімає RXNE — окремого квитування немає. */
        const uint8_t byte = LL_USART_ReceiveData8(USART1);

        if (ring_buffer_push_isr(&s_rx_ring, byte)) {
            s_stats.bytes_received++;
        } else {
            /* Кільце повне. Байт втрачено — але СВІДОМО й за сталий час,
             * а не через зависання обробника в очікуванні місця. */
            s_stats.ring_overflows++;
        }
        signal_consumer = true;
    }

    if (signal_consumer && s_consumer != NULL) {
        /* Версія з суфіксом FromISR ніколи не блокує: вона лише зводить
         * лічильник сповіщень завдання і каже, чи треба перемкнути контекст. */
        vTaskNotifyGiveFromISR(s_consumer, &higher_priority_woken);
    }

    const uint32_t spent = DWT->CYCCNT - entry_cycles; /* переповнення 32 біт коректне */
    if (spent > s_stats.worst_cycles) {
        s_stats.worst_cycles = spent;
    }

    /* Якщо розбуджене завдання пріоритетніше за перерване — перемикаємось
     * прямо на виході з переривання, не чекаючи наступного SysTick. */
    portYIELD_FROM_ISR(higher_priority_woken);
}

/* ---------------------------------------------------------------------------
 * НИЖНЯ ПОЛОВИНА. Тут дозволено все, що заборонено вище: цикли за даними,
 * побітова CRC, очікування на події.
 * ------------------------------------------------------------------------ */
static void apply_frame(const uint8_t *payload, uint8_t len)
{
    /* Місце застосунку: команда з кадру доїжджає до логіки пристрою.
     * Для прикладу — байт 0 як код команди, решта як аргументи. */
    if (len >= 1u && payload[0] == 0x01u) {
        /* 0x01 = «підтвердь зв'язок»: оновлюємо мітку останнього кадру. */
        (void)timer_ms_ticks();
    }
}

static void uart_processing_task(void *arg)
{
    (void)arg;

    frame_parser_init(&s_parser);

    for (;;) {
        /* Чекаємо сповіщення в стані Blocked: жодного такту процесора,
         * поки байтів немає. Тайм-аут — щоб раз на секунду прокинутись
         * навіть у тиші й помітити, що лінія замовкла. */
        (void)ulTaskNotifyTake(pdTRUE, pdMS_TO_TICKS(1000));

        uint8_t byte;
        uint8_t frame_len;

        /* Вичерпуємо кільце ДО ДНА. Сповіщення бінарне за змістом:
         * поки ми розбирали кадр, ISR могла покласти ще десяток байтів,
         * і другого сповіщення на них може не бути. */
        while (ring_buffer_pop_main(&s_rx_ring, &byte)) {
            if (frame_parser_feed(&s_parser, byte, &frame_len)) {
                apply_frame(s_parser.payload, frame_len);
            }
        }
    }
}

void uart_bridge_start(void)
{
    ring_buffer_init(&s_rx_ring);

    s_stats.bytes_received = 0u;
    s_stats.ring_overflows = 0u;
    s_stats.hw_overruns = 0u;
    s_stats.worst_cycles = 0u;

    /* Дескриптор завдання мусить існувати ДО того, як переривання дозволено:
     * інакше перший же байт прийде на s_consumer == NULL. Виклик
     * NVIC_EnableIRQ у main() навмисно стоїть після цього рядка. */
    s_consumer = xTaskCreateStatic(uart_processing_task,
                                   "uart-rx",
                                   UART_TASK_STACK_WORDS,
                                   NULL,
                                   configMAX_PRIORITIES - 2u,
                                   s_task_stack,
                                   &s_task_tcb);
    configASSERT(s_consumer != NULL);
}

const uart_isr_stats_t *uart_bridge_stats(void)
{
    return &s_stats;
}
