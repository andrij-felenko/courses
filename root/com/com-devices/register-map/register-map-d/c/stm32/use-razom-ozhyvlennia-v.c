#include "stm32f4xx_hal.h"

extern I2C_HandleTypeDef hi2c1;     // ініціалізований у MX_I2C1_Init()

// --- адреси з даташита MPU-6050 ---
#define ADDR        (0x68 << 1)     // HAL чекає 8-бітову адресу: 7 біт зсунуті вліво
#define REG_WHO     0x75            // WHO_AM_I
#define EXPECTED_ID 0x68            // сталий код саме цього чіпа
#define REG_PWR     0x6B            // PWR_MGMT_1
#define REG_CFG     0x1C            // ACCEL_CONFIG (діапазон у бітах 4:3)
#define REG_XOUT_H  0x3B            // старший байт виміру осі X

// прочитати один байт регістра reg
static uint8_t read_reg(uint8_t reg) {
    uint8_t val = 0;
    // Mem_Read і є шаблон «номер регістра, повторний старт, читання»
    HAL_I2C_Mem_Read(&hi2c1, ADDR, reg, I2C_MEMADD_SIZE_8BIT, &val, 1, 100);
    return val;
}

// записати один байт val у регістр reg
static void write_reg(uint8_t reg, uint8_t val) {
    HAL_I2C_Mem_Write(&hi2c1, ADDR, reg, I2C_MEMADD_SIZE_8BIT, &val, 1, 100);
}
