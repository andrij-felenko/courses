#include "stm32f4xx_hal.h"
#include <stdio.h>

extern SPI_HandleTypeDef hspi1;   // швидкість, MSB-first і режим — у CubeMX

#define CS_PORT GPIOA
#define CS_PIN  GPIO_PIN_4        // вибір пристрою: звичайний GPIO, смикаємо вручну

// прочитати один регістр: шлемо адресу, приймаємо відповідь
static uint8_t spi_read_reg(uint8_t reg) {
    uint8_t tx[2] = { reg | 0x80, 0x00 };   // старший біт = «читання» (типово)
    uint8_t rx[2] = { 0 };
    HAL_GPIO_WritePin(CS_PORT, CS_PIN, GPIO_PIN_RESET);  // «слухай мене»
    HAL_SPI_TransmitReceive(&hspi1, tx, rx, 2, 100);     // шлемо й приймаємо разом
    HAL_GPIO_WritePin(CS_PORT, CS_PIN, GPIO_PIN_SET);    // «все, відпускаю»
    return rx[1];                           // відповідь прийшла в другому байті
}

int main(void) {
    HAL_Init(); SystemClock_Config(); MX_GPIO_Init(); MX_SPI1_Init(); MX_USART2_UART_Init();
    HAL_GPIO_WritePin(CS_PORT, CS_PIN, GPIO_PIN_SET);    // спокій = не вибрано

    while (1) {
        printf("%02X\r\n", spi_read_reg(0x0F));          // умовний регістр «хто ти»
        HAL_Delay(500);
    }
}
