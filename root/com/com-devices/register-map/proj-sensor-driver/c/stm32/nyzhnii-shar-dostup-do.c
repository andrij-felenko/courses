#include "stm32f4xx_hal.h"

extern I2C_HandleTypeDef hi2c1;              // готує CubeMX: MX_I2C1_Init()

#define MPU_ADDR     (0x68 << 1)             // HAL чекає 8-бітову адресу зі зсувом
#define REG_WHO      0x75
#define REG_PWR      0x6B
#define REG_CFG      0x1C
#define REG_XOUT_H   0x3B
#define MPU_OK       HAL_OK
#define MPU_WAIT     100                     // стеля очікування обміну, мс

// записати один байт val у регістр reg; повертає HAL_StatusTypeDef
static HAL_StatusTypeDef mpu_write(uint8_t reg, uint8_t val) {
    return HAL_I2C_Mem_Write(&hi2c1, MPU_ADDR, reg, I2C_MEMADD_SIZE_8BIT,
                             &val, 1, MPU_WAIT);
}

// прочитати n байтів поспіль від reg у buf; повертає HAL_StatusTypeDef
static HAL_StatusTypeDef mpu_read(uint8_t reg, uint8_t *buf, uint16_t n) {
    // Mem_Read сам видає повторний старт після номера регістра
    return HAL_I2C_Mem_Read(&hi2c1, MPU_ADDR, reg, I2C_MEMADD_SIZE_8BIT,
                            buf, n, MPU_WAIT);
}
