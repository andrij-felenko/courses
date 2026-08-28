#include "stm32f4xx_hal.h"

extern I2C_HandleTypeDef hi2c1;             // налаштований у MX_I2C1_Init()

// HAL чекає 8-бітну адресу: 7-бітну зсуваємо вліво, молодший біт — R/W.
#define MS5611_ADDR   (0x77 << 1)           // (0x76 << 1), якщо CSB на VCC
#define I2C_TMO       100                   // мс на транзакцію

#define CMD_RESET      0x1E
#define CMD_CONV_D1    0x40                 // тиск;   до цього додається OSR·2
#define CMD_CONV_D2    0x50                 // темпер.; до цього додається OSR·2
#define CMD_ADC_READ   0x00
#define CMD_PROM_BASE  0xA0                 // A0..AE — 8 слів по 16 біт

// Тут зберігатимемо весь PROM: [0]=reserved+CRC-nibble, [1..6]=C1..C6, [7]=serial+CRC.
uint16_t g_prom[8];

// Скид давача.
static bool ms5611_reset(void) {
  uint8_t cmd = CMD_RESET;
  if (HAL_I2C_Master_Transmit(&hi2c1, MS5611_ADDR, &cmd, 1, I2C_TMO) != HAL_OK) return false;
  HAL_Delay(5);            // ~2.8 мс на перезавантаження PROM у регістри
  return true;
}

// Прочитати одне 16-бітне слово PROM за індексом 0..7.
static bool ms5611_read_prom_word(uint8_t index, uint16_t *out) {
  uint8_t cmd = CMD_PROM_BASE + index * 2;  // A0, A2, A4, ... AE
  uint8_t buf[2];
  if (HAL_I2C_Master_Transmit(&hi2c1, MS5611_ADDR, &cmd, 1, I2C_TMO) != HAL_OK) return false;
  if (HAL_I2C_Master_Receive(&hi2c1, MS5611_ADDR, buf, 2, I2C_TMO) != HAL_OK) return false;
  *out = ((uint16_t)buf[0] << 8) | buf[1];  // старший байт першим
  return true;
}

// Прочитати весь PROM (8 слів) у g_prom[]. Викликається раз при старті.
static bool ms5611_read_prom(void) {
  for (uint8_t i = 0; i < 8; i++) {
    if (!ms5611_read_prom_word(i, &g_prom[i])) return false;
  }
  return true;
}
