#include "trace.h"

#include <stddef.h>

#include "stm32f4xx.h"

/* USART2 висить на APB1; для типової конфігурації STM32F4 на 168 МГц це 42 МГц. */
#define TRACE_APB1_HZ 42000000u
#define TRACE_BAUD    115200u

/*
 * Стеля очікування замість while(!TXE). Якщо тактування USART зникло або
 * периферію збило тим самим збоєм, що привів нас у обробник, нескінченне
 * очікування перетворило б аварійний звіт на друге зависання.
 */
#define TRACE_SPIN_MAX 300000u

static void trace_put(uint8_t byte)
{
    uint32_t spin = TRACE_SPIN_MAX;

    while ((USART2->SR & USART_SR_TXE) == 0u) {
        if (--spin == 0u) {
            return; /* лінія мертва — мовчки губимо байт, але не вішаємо чип */
        }
    }
    USART2->DR = byte;
}

void trace_init(void)
{
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN;
    RCC->APB1ENR |= RCC_APB1ENR_USART2EN;
    __DSB(); /* дочекатися, доки запис у RCC дійде до шини, перш ніж чіпати периферію */

    /* PA2 і PA3 у режим альтернативної функції (MODER = 0b10 на пін). */
    GPIOA->MODER &= ~((3u << (2u * 2u)) | (3u << (3u * 2u)));
    GPIOA->MODER |= (2u << (2u * 2u)) | (2u << (3u * 2u));

    /* AF7 = USART2 для обох пінів (AFR[0], по 4 біти на пін). */
    GPIOA->AFR[0] &= ~((0xFu << (2u * 4u)) | (0xFu << (3u * 4u)));
    GPIOA->AFR[0] |= (7u << (2u * 4u)) | (7u << (3u * 4u));

    /* Дільник для oversampling 16: округлюємо до найближчого цілого. */
    USART2->BRR = (TRACE_APB1_HZ + (TRACE_BAUD / 2u)) / TRACE_BAUD;
    USART2->CR1 = USART_CR1_TE | USART_CR1_RE | USART_CR1_UE;
    USART2->CR2 = 0u;
    USART2->CR3 = 0u;
}

void trace_char(char c)
{
    trace_put((uint8_t)c);
}

void trace_str(const char *text)
{
    if (text == NULL) {
        return;
    }
    /* Обмеження довжини: у кадрі аварії покажчик може вести в сміття. */
    for (uint32_t i = 0u; i < 256u && text[i] != '\0'; ++i) {
        trace_put((uint8_t)text[i]);
    }
}

void trace_hex32(uint32_t value)
{
    static const char digits[] = "0123456789ABCDEF";

    trace_put('0');
    trace_put('x');
    for (int shift = 28; shift >= 0; shift -= 4) {
        trace_put((uint8_t)digits[(value >> shift) & 0xFu]);
    }
}

void trace_kv(const char *name, uint32_t value)
{
    trace_str(name);
    trace_put('=');
    trace_hex32(value);
    trace_str("\r\n");
}

int trace_getc(void)
{
    if ((USART2->SR & USART_SR_RXNE) == 0u) {
        return -1;
    }
    return (int)(USART2->DR & 0xFFu);
}

void trace_flush(void)
{
    uint32_t spin = TRACE_SPIN_MAX;

    while ((USART2->SR & USART_SR_TC) == 0u) {
        if (--spin == 0u) {
            return;
        }
    }
}
