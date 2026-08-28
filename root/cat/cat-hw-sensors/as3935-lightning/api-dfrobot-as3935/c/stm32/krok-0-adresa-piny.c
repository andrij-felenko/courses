#include "stm32f4xx_hal.h"
#include <stdbool.h>

// ── Плата: під свій мікроконтролер ─────────────────────────────
#define IRQ_PORT             GPIOB
#define IRQ_PIN              GPIO_PIN_0   // пін з вільною лінією EXTI0
#define AS3935_ADDR          (0x03 << 1)  // HAL чекає 8-бітну адресу: 7 біт ≪ 1

// ── Налаштування під місце ─────────────────────────────────────
#define AS3935_CAPACITANCE   96           // стартова ємність, пФ (кратна 8)

extern I2C_HandleTypeDef hi2c1;   // CubeMX: 400 кГц (підтяжки вже на модулі)
extern TIM_HandleTypeDef htim2;   // лічильник фронтів LCO для калібрування

volatile bool irqTriggered = false;   // прапорець із обробника переривання

// Готової бібліотеки нема — говоримо з чіпом його регістрами напряму.
static HAL_StatusTypeDef as3935_write(uint8_t reg, uint8_t val) {
    return HAL_I2C_Mem_Write(&hi2c1, AS3935_ADDR, reg,
                             I2C_MEMADD_SIZE_8BIT, &val, 1, 100);
}
static HAL_StatusTypeDef as3935_read(uint8_t reg, uint8_t *val) {
    return HAL_I2C_Mem_Read(&hi2c1, AS3935_ADDR, reg,
                            I2C_MEMADD_SIZE_8BIT, val, 1, 100);
}
