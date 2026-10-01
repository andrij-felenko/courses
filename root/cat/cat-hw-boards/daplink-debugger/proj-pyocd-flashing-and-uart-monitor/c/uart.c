#include "uart.h"

// Фізичні базові адреси периферійних блоків ARM Cortex-M (STM32)
#define PERIPH_BASE       0x40000000U
#define APB2PERIPH_BASE   (PERIPH_BASE + 0x00010000U)
#define AHBPERIPH_BASE    (PERIPH_BASE + 0x00020000U)

#define RCC_BASE          (AHBPERIPH_BASE + 0x00001000U)
#define GPIOA_BASE        (APB2PERIPH_BASE + 0x00000800U)
#define USART1_BASE       (APB2PERIPH_BASE + 0x00003800U)

// Структури опису регістрів системної периферії
typedef struct {
    volatile uint32_t CR;
    volatile uint32_t CFGR;
    volatile uint32_t CIR;
    volatile uint32_t APB2RSTR;
    volatile uint32_t APB1RSTR;
    volatile uint32_t AHBENR;
    volatile uint32_t APB2ENR;
    volatile uint32_t APB1ENR;
} RCC_Regs_t;

typedef struct {
    volatile uint32_t CRL;
    volatile uint32_t CRH;
    volatile uint32_t IDR;
    volatile uint32_t ODR;
    volatile uint32_t BSRR;
    volatile uint32_t BRR;
    volatile uint32_t LCKR;
} GPIO_Regs_t;

typedef struct {
    volatile uint32_t SR;   // Статус-регістр
    volatile uint32_t DR;   // Регістр даних
    volatile uint32_t BRR;  // Регістр вибору швидкості
    volatile uint32_t CR1;  // Регістр керування 1
    volatile uint32_t CR2;  // Регістр керування 2
    volatile uint32_t CR3;  // Регістр керування 3
    volatile uint32_t GTPR; // Регістр тактування
} USART_Regs_t;

#define RCC    ((RCC_Regs_t *) RCC_BASE)
#define GPIOA  ((GPIO_Regs_t *) GPIOA_BASE)
#define USART1 ((USART_Regs_t *) USART1_BASE)

// Бітові маски системних регістрів
#define RCC_APB2ENR_IOPAEN   (1U << 2)   // Тактування порту GPIOA
#define RCC_APB2ENR_USART1EN (1U << 14)  // Тактування інтерфейсу USART1

#define USART_CR1_RE   (1U << 2)   // Дозвіл прийому (Receiver Enable)
#define USART_CR1_TE   (1U << 3)   // Дозвіл передачі (Transmitter Enable)
#define USART_CR1_UE   (1U << 13)  // Активація модуля USART (USART Enable)

#define USART_SR_RXNE  (1U << 5)   // Прапорець наявності даних для читання
#define USART_SR_TXE   (1U << 7)   // Прапорець готовності буфера передачі

#ifndef F_CPU
#define F_CPU 72000000U // Тактова частота шини APB2 за замовчуванням (72 МГц)
#endif

void uart_init(uint32_t baudrate) {
    if (baudrate == 0) {
        baudrate = UART_DEFAULT_BAUDRATE;
    }

    // 1. Вмикаємо тактування GPIOA та USART1 через регістр APB2ENR
    RCC->APB2ENR |= (RCC_APB2ENR_IOPAEN | RCC_APB2ENR_USART1EN);

    // 2. Налаштування режимів виводів GPIOA для USART1:
    // PA9  (TX): Альтернативна функція Push-Pull, 50 МГц (CRH[7:4] = 0b1011)
    // PA10 (RX): Вхід у плаваючому режимі / Floating input (CRH[11:8] = 0b0100)
    GPIOA->CRH &= ~(0xFFU << 4);
    GPIOA->CRH |= (0xBU << 4);  // PA9 TX
    GPIOA->CRH |= (0x4U << 8);  // PA10 RX

    // 3. Обчислення значення виділеного регістру швидкості (BRR)
    uint32_t usartdiv = (F_CPU + (baudrate / 2U)) / baudrate;
    USART1->BRR = usartdiv;

    // 4. Активація передавача, приймача та вмикання самого модуля USART1
    USART1->CR1 = 0;
    USART1->CR1 |= (USART_CR1_TE | USART_CR1_RE | USART_CR1_UE);
}

void uart_send_char(char c) {
    uint32_t timeout = 1000000U;
    // Очікування очищення буфера передавача (TXE)
    while (!(USART1->SR & USART_SR_TXE)) {
        if (--timeout == 0) return; // Захист від зациклення у випадку апаратної помилки
    }
    USART1->DR = (uint8_t)c;
}

void uart_send_string(const char *str) {
    if (!str) return;
    while (*str) {
        uart_send_char(*str++);
    }
}

void uart_send_buffer(const uint8_t *data, size_t length) {
    if (!data) return;
    for (size_t i = 0; i < length; i++) {
        uart_send_char((char)data[i]);
    }
}

bool uart_receive_char(char *out_c) {
    if (!out_c) return false;

    // Перевірка наявності символу в буфері прийому (RXNE)
    if (USART1->SR & USART_SR_RXNE) {
        *out_c = (char)(USART1->DR & 0xFFU);
        return true;
    }
    return false;
}
