/*
 * Пастка наївного вимкнення: вкладена функція драйвера сліпо вмикає
 * переривання й знімає захист із зовнішньої критичної секції.
 * Код робочий — і саме тому небезпечний: він передає пакет, але не захищає його.
 */
#include <stddef.h>
#include <stdint.h>

#include "cortexm.h"
#include "demos.h"

/* STM32F4: USART1 за адресою 0x40011000. */
typedef struct {
    volatile uint32_t SR;  /* 0x00 — стан */
    volatile uint32_t DR;  /* 0x04 — дані */
    volatile uint32_t BRR; /* 0x08 — дільник швидкості */
    volatile uint32_t CR1; /* 0x0C — керування */
} usart_regs_t;

#define USART1 ((usart_regs_t *)0x40011000UL)
#define USART_SR_TXE (1U << 7)

#define PACKET_HEADER 0xA5U

/* CRC-8, поліном 0x07 — той самий, що в більшості телеметричних кадрів. */
static uint8_t packet_crc8(const uint8_t *payload, size_t len)
{
    uint8_t crc = 0xFFU;

    for (size_t i = 0U; i < len; i++) {
        crc ^= payload[i];
        for (uint8_t bit = 0U; bit < 8U; bit++) {
            crc = ((crc & 0x80U) != 0U) ? (uint8_t)((uint8_t)(crc << 1) ^ 0x07U)
                                        : (uint8_t)(crc << 1);
        }
    }
    return crc;
}

/* Низький рівень драйвера: власна критична секція навколо регістра даних. */
static void uart_send_byte(uint8_t byte)
{
    __disable_irq();

    /* Друга вада на додачу до головної: очікування апаратури всередині
     * вимкнених переривань. На 115200 порожній передавач — це до 87 мкс. */
    while ((USART1->SR & USART_SR_TXE) == 0U) {
    }
    USART1->DR = byte;

    __enable_irq(); /* ПОМИЛКА: CPSIE i хай що було до входу */
}

/* Високий рівень: хоче віддати весь пакет неподільно. */
int telemetry_send_packet(const uint8_t *payload, size_t len)
{
    if (payload == NULL || len == 0U || len > 255U) {
        return -1;
    }

    __disable_irq(); /* зовнішня критична секція */

    const uint8_t crc = packet_crc8(payload, len);
    uart_send_byte(PACKET_HEADER); /* вкладений виклик — і захисту вже немає */

    /*
     * Звідси й до кінця функції переривання УВІМКНЕНІ, хоча автор коду певен,
     * що сидить у критичній секції. ISR вклинюється між байтами й пише в той
     * самий DR — приймач дістає перемішаний кадр.
     */
    for (size_t i = 0U; i < len; i++) {
        while ((USART1->SR & USART_SR_TXE) == 0U) {
        }
        USART1->DR = payload[i];
    }

    while ((USART1->SR & USART_SR_TXE) == 0U) {
    }
    USART1->DR = crc;

    __enable_irq();
    return 0;
}
