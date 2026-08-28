#include <stdint.h>
#include <stdbool.h>

/* Базові адреси периферійних блоків за Reference Manual */
#define PERIPH_BASE           (0x40000000UL)
#define APB2PERIPH_BASE       (PERIPH_BASE + 0x00010000UL)
#define USART1_BASE           (APB2PERIPH_BASE + 0x00003800UL)
#define DBGMCU_BASE           (0xE0042000UL)

/* Бітові маски регістрів USART */
#define USART_CR1_UE          (1UL << 0)   /* Увімкнення блока USART */
#define USART_CR1_TE          (1UL << 3)   /* Увімкнення передавача (Transmitter Enable) */
#define USART_ISR_TXE         (1UL << 7)   /* Буфер передачі вільний (Transmit Data Empty, RO) */
#define USART_ISR_TC          (1UL << 6)   /* Передачу завершено (Transmission Complete, W1C) */
#define USART_ICR_TCCF        (1UL << 6)   /* Очищення прапорця завершення передачі (Write 1 to Clear) */

/* Структура регістрової карти USART із точним зміщенням змісту за RM */
typedef struct {
    volatile uint32_t CR1;    /* Offset: 0x00 - Control Register 1 */
    volatile uint32_t CR2;    /* Offset: 0x04 - Control Register 2 */
    volatile uint32_t CR3;    /* Offset: 0x08 - Control Register 3 */
    volatile uint32_t BRR;    /* Offset: 0x0C - Baud Rate Register */
    volatile uint32_t GTPR;   /* Offset: 0x10 - Guard Time and Prescaler */
    volatile uint32_t RTOR;   /* Offset: 0x14 - Receiver Timeout */
    volatile uint32_t RQR;    /* Offset: 0x18 - Request Register */
    volatile uint32_t ISR;    /* Offset: 0x1C - Interrupt and Status Register (RO / W1C flags) */
    volatile uint32_t ICR;    /* Offset: 0x20 - Interrupt Flag Clear Register (WO / W1C) */
    volatile uint32_t RDR;    /* Offset: 0x24 - Receive Data Register (RO) */
    volatile uint32_t TDR;    /* Offset: 0x28 - Transmit Data Register (WO) */
} UsartRegisters;

/* Регістр ідентифікації кремнію для визначення ревізії чипа (DBGMCU_IDCODE) */
typedef struct {
    volatile uint32_t IDCODE; /* Offset: 0x00 - Device ID [11:0] та Silicon Revision [31:16] */
} DbgMcuRegisters;

#define USART1   ((UsartRegisters *)USART1_BASE)
#define DBGMCU   ((DbgMcuRegisters *)DBGMCU_BASE)

/* Зчитування ревізії кремнію: 0x1000 = Rev A (з багом), 0x2000 = Rev B (виправлений) */
static inline uint16_t get_silicon_revision(void) {
    return (uint16_t)(DBGMCU->IDCODE >> 16);
}

/* Ініціалізація передавача UART */
void usart_init_tx(uint32_t pclk_hz, uint32_t baudrate) {
    /* 1. Обчислення та запис дільника швидкості (Baud Rate) */
    uint32_t brr_val = (pclk_hz + (baudrate / 2U)) / baudrate;
    USART1->BRR = brr_val;

    /* 2. Конфігурація: вмикаємо блок і передавач */
    USART1->CR1 = USART_CR1_UE | USART_CR1_TE;

    /* 3. Апаратний обхід (Workaround) з Errata Sheet для ревізії Rev A:
     * Потрібна пауза на 1 такт шини після увімкнення TE перед першим записом */
    if (get_silicon_revision() == 0x1000U) {
        __asm__ volatile ("nop");
    }
}

/* Відправка одного байта з блокуючим очікуванням готовності буфера */
bool usart_send_byte(uint8_t byte, uint32_t timeout_cycles) {
    /* Очікуємо готовності передавального буфера (прапорець TXE) */
    while (!(USART1->ISR & USART_ISR_TXE)) {
        if (timeout_cycles == 0) {
            return false; /* Захист від вічного зависання при апаратній аварії */
        }
        timeout_cycles--;
    }

    /* Запис байта в регістр даних передавача */
    USART1->TDR = byte;
    return true;
}

/* Безпечне очищення прапорця завершення передачі TC через механізм W1C */
void usart_clear_tc_flag(void) {
    /* Запис 1 у біт TCCF регістра ICR очищає біт TC у регістрі ISR.
     * Ніякого Read-Modify-Write (RMW) над ISR не виконується! */
    USART1->ICR = USART_ICR_TCCF;
}
