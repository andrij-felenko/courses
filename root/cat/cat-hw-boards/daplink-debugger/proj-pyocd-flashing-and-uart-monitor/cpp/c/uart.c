#include "uart.h"

// Регістри системи тактування (RCC) та порту GPIOA для C-реалізації
typedef struct {
    volatile uint32_t CR;
    volatile uint32_t PLLCFGR;
    volatile uint32_t CFGR;
    volatile uint32_t CIR;
    volatile uint32_t AHB1ENR;
    volatile uint32_t AHB2ENR;
    volatile uint32_t AHB3ENR;
    uint32_t RESERVED0;
    volatile uint32_t APB1ENR;
    volatile uint32_t APB2ENR;
} RCC_Regs_t;

typedef struct {
    volatile uint32_t MODER;
    volatile uint32_t OTYPER;
    volatile uint32_t OSPEEDR;
    volatile uint32_t PUPDR;
    volatile uint32_t IDR;
    volatile uint32_t ODR;
    volatile uint32_t BSRR;
    volatile uint32_t LCKR;
    volatile uint32_t AFR[2];
} GPIO_Regs_t;

#define RCC_BASE_ADDR   ((uintptr_t)0x40023800U)
#define GPIOA_BASE_ADDR ((uintptr_t)0x40020000U)

#define USART_SR_TXE    (1U << 7)
#define USART_SR_TC     (1U << 6)

#define USART_CR1_UE    (1U << 13)
#define USART_CR1_TE    (1U << 3)
#define USART_CR1_RE    (1U << 2)

void uart_init(USART_Registers_t* usart, uint32_t pclk_freq, uint32_t baud_rate) {
    if (!usart || baud_rate == 0 || pclk_freq == 0) {
        return;
    }

    RCC_Regs_t* rcc = (RCC_Regs_t*)RCC_BASE_ADDR;
    GPIO_Regs_t* gpioa = (GPIO_Regs_t*)GPIOA_BASE_ADDR;

    // 1. Ввімкнення тактування порту GPIOA та USART2
    rcc->AHB1ENR |= (1U << 0);  // GPIOAEN
    rcc->APB1ENR |= (1U << 17); // USART2EN

    // 2. Конфігурація виводів PA2 (TX) та PA3 (RX) у режим альтернативної функції AF7
    gpioa->MODER &= ~((3U << (2 * 2)) | (3U << (2 * 3)));
    gpioa->MODER |=  ((2U << (2 * 2)) | (2U << (2 * 3)));

    gpioa->AFR[0] &= ~((0xFU << (4 * 2)) | (0xFU << (4 * 3)));
    gpioa->AFR[0] |=  ((7U    << (4 * 2)) | (7U    << (4 * 3)));

    gpioa->OSPEEDR |= ((3U << (2 * 2)) | (3U << (2 * 3)));

    // 3. Обчислення дільника швидкості BRR
    uint32_t usart_div = (pclk_freq + (baud_rate / 2U)) / baud_rate;
    usart->BRR = usart_div;

    // 4. Активація модуля UART, передавача та приймача
    usart->CR1 = USART_CR1_UE | USART_CR1_TE | USART_CR1_RE;
}

void uart_write_char(USART_Registers_t* usart, char ch) {
    // Перевірка порожності буфера передачі (TXE)
    while (!(usart->SR & USART_SR_TXE)) {
        // Очікування
    }

    usart->DR = (uint8_t)ch;
}

void uart_write_string(USART_Registers_t* usart, const char* str) {
    if (!str) return;

    while (*str) {
        uart_write_char(usart, *str++);
    }
}

void uart_println(USART_Registers_t* usart, const char* str) {
    uart_write_string(usart, str);
    uart_write_char(usart, '\r');
    uart_write_char(usart, '\n');
}

void uart_flush(USART_Registers_t* usart) {
    // Перевірка прапорця повного завершення передачі (TC)
    while (!(usart->SR & USART_SR_TC)) {
        // Очікування
    }
}
