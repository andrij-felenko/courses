#include "stm32f4xx_hal.h"
#include <stdio.h>

extern I2C_HandleTypeDef hi2c1;

#define ADDR    (0x76 << 1)     // HAL бере 8-бітову адресу: 7 бітів зсунуті вліво
#define REG_ID  0xD0            // регістр «хто ти»
#define REG_OUT 0xF7            // старший байт виміру

// Mem_Read сам робить «назвати регістр → повторний старт → читати»
static HAL_StatusTypeDef i2c_read(uint8_t reg, uint8_t *buf, uint16_t n) {
    return HAL_I2C_Mem_Read(&hi2c1, ADDR, reg, I2C_MEMADD_SIZE_8BIT, buf, n, 100);
}

int main(void) {
    HAL_Init(); SystemClock_Config(); MX_I2C1_Init(); MX_USART2_UART_Init();

    uint8_t id = 0;
    if (i2c_read(REG_ID, &id, 1) == HAL_OK) printf("ID = %02X\r\n", id);
    else                                    printf("немає відповіді\r\n");

    while (1) {
        uint8_t raw[2];
        if (i2c_read(REG_OUT, raw, 2) == HAL_OK)
            printf("%d\r\n", (raw[0] << 8) | raw[1]);   // старший байт першим
        HAL_Delay(500);
    }
}
