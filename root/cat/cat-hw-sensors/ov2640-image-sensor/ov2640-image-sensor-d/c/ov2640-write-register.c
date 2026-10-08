#include "stm32f4xx_hal.h"
#include <stdbool.h>

#define OV2640_SCCB_ADDR 0x60 // 8-бітна адреса запису OV2640

extern I2C_HandleTypeDef hi2c1;

// Запис значення в регістр OV2640 з вибором банку
bool ov2640_write_register(uint8_t bank, uint8_t reg, uint8_t value) {
    uint8_t data[2];
    
    // Перемикання банку регістрів (регістр 0xFF)
    data[0] = 0xFF;
    data[1] = bank;
    if (HAL_I2C_Master_Transmit(&hi2c1, OV2640_SCCB_ADDR, data, 2, 100) != HAL_OK) {
        return false;
    }
    
    // Запис цільового значення в регістр
    data[0] = reg;
    data[1] = value;
    if (HAL_I2C_Master_Transmit(&hi2c1, OV2640_SCCB_ADDR, data, 2, 100) != HAL_OK) {
        return false;
    }
    
    return true;
}

// Переведення в програмний режим Standby
bool ov2640_set_standby(bool enable) {
    // Регістр 0x09 знаходиться в Bank 1
    if (!ov2640_write_register(0x01, 0x09, enable ? 0x10 : 0x00)) {
        return false;
    }
    return true;
}
