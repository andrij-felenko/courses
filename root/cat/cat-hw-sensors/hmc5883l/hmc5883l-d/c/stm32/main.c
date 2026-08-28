#include "stm32f4xx_hal.h"

#define HMC  (0x1E << 1)   // HAL бере 8-бітну адресу: 7 біт адреси + біт напряму

extern I2C_HandleTypeDef hi2c1;   // налаштований у CubeMX на 100 кГц

static HAL_StatusTypeDef hmc_write_reg(uint8_t reg, uint8_t val) {
    return HAL_I2C_Mem_Write(&hi2c1, HMC, reg, I2C_MEMADD_SIZE_8BIT,
                             &val, 1, HAL_MAX_DELAY);
}

HAL_StatusTypeDef hmc_init(void) {
    if (hmc_write_reg(0x00, 0x70) != HAL_OK) return HAL_ERROR;  // Config A: 8 усереднень, 15 Гц
    if (hmc_write_reg(0x01, 0x20) != HAL_OK) return HAL_ERROR;  // Config B: підсилення ±1.3 Гаус
    return hmc_write_reg(0x02, 0x00);                           // Mode: безперервний вимір
}

HAL_StatusTypeDef hmc_read(int16_t *x, int16_t *y, int16_t *z) {
    uint8_t b[6];                                 // 6 байтів: X, Z, Y (саме такий порядок!)
    HAL_StatusTypeDef st = HAL_I2C_Mem_Read(&hi2c1, HMC, 0x03, I2C_MEMADD_SIZE_8BIT,
                                            b, sizeof(b), HAL_MAX_DELAY);
    if (st != HAL_OK) return st;
    *x = (int16_t)((b[0] << 8) | b[1]);
    *z = (int16_t)((b[2] << 8) | b[3]);           // Z йде ДРУГИМ, не третім
    *y = (int16_t)((b[4] << 8) | b[5]);
    return HAL_OK;
}
