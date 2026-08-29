/* Складання драйвера докупи: підняти USART1, відрапортувати ревізію
 * кремнію в лінію й далі відлунювати все, що прийшло.
 */
#include <stdint.h>
#include <string.h>

#include "silicon_rev.h"
#include "usart_driver.h"

/* Частота APB2 після скидання й швидкість лінії. Обидва числа беруться з
 * налаштування тактового дерева, а не вгадуються: помилка тут дає рівно
 * ті самі «ієрогліфи в терміналі», що й неправильний дільник. */
#define PCLK2_HZ  64000000UL
#define BAUDRATE  115200UL

/* Дозвіл переривання в контролері NVIC. Номер вектора USART1 — з таблиці
 * векторів переривань у Reference Manual. */
#define NVIC_ISER0   (*(volatile uint32_t *)0xE000E100UL)
#define USART1_IRQn  27U

static usart_t uart;

static void emit(const char *text)
{
    size_t sent = 0U;
    (void)usart_send(&uart, (const uint8_t *)text, strlen(text), &sent);
    /* Скільки саме байтів вийшло, тут не питаємо: єдиний споживач цього
     * рядка — людина в терміналі, обірваний рядок вона побачить сама. */
}

static void echo_byte(uint8_t byte)
{
    /* Відлуння прямо в обробнику: один байт у порожній буфер передачі
     * лягає без очікування. Довші відповіді з обробника не шлють — там
     * би довелося крутити цикл очікування з піднятим пріоритетом. */
    if (uart.regs->ISR & USART_ISR_TXE) {
        uart.regs->TDR = (uint32_t)byte & USART_TDR_MASK;
    }
}

/* Вектор переривання USART1 з таблиці векторів */
void USART1_IRQHandler(void)
{
    usart_irq_handler(&uart, echo_byte);
}

int main(void)
{
    if (usart_init_tx(&uart, USART1, PCLK2_HZ, BAUDRATE) != USART_OK) {
        /* Швидкість недосяжна від цієї шини: сказати про це нема чим —
         * зламаний саме той канал, яким доповідають про поломки. */
        for (;;) {
        }
    }

    switch (silicon_revision()) {
    case SILICON_REV_A:
        emit("silicon Rev A: обхід дефекту TE увімкнено\r\n");
        break;
    case SILICON_REV_B:
        emit("silicon Rev B: дефект TE усунено в кремнії\r\n");
        break;
    default:
        emit("невідомий кремній: обхід дефекту TE увімкнено про всяк\r\n");
        break;
    }

    /* Дочекатися, поки рядок фізично вийде в лінію, і погасити TC:
     * далі ми дозволяємо переривання, і чужий TC у ньому лише збивав би. */
    (void)usart_flush(&uart);

    usart_enable_rx_irq(&uart);
    NVIC_ISER0 = 1UL << USART1_IRQn;

    for (;;) {
        /* Помилки лінії знімає головний цикл, а не обробник: доповідь про
         * переповнення сама займає лінію, а робити це з переривання —
         * означає доповідати про затримку, стоячи в затримці. */
        const uint32_t errors = usart_take_errors(&uart);

        if (errors & USART_ISR_ORE) {
            emit("overrun: байт втрачено\r\n");
        }
        if (errors & USART_ISR_NF) {
            emit("noise: шум у лінії\r\n");
        }
        if (errors & USART_ISR_FE) {
            emit("framing: збита швидкість або обірваний кадр\r\n");
        }
        if (errors & USART_ISR_PE) {
            emit("parity: биті дані\r\n");
        }
    }
}
