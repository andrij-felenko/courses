#include "driver/i2c.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define I2C_PORT      I2C_NUM_0
#define MS5611_ADDR   0x77          // 0x76, якщо CSB на VCC
#define I2C_TMO       pdMS_TO_TICKS(100)

#define CMD_RESET      0x1E
#define CMD_CONV_D1    0x40         // тиск;   до цього додається OSR·2
#define CMD_CONV_D2    0x50         // темпер.; до цього додається OSR·2
#define CMD_ADC_READ   0x00
#define CMD_PROM_BASE  0xA0         // A0..AE — 8 слів по 16 біт

// Тут зберігатимемо весь PROM: [0]=reserved+CRC-nibble, [1..6]=C1..C6, [7]=serial+CRC.
uint16_t g_prom[8];

// Скид давача.
static esp_err_t ms5611_reset(void) {
    uint8_t cmd = CMD_RESET;
    esp_err_t err = i2c_master_write_to_device(I2C_PORT, MS5611_ADDR, &cmd, 1, I2C_TMO);
    vTaskDelay(pdMS_TO_TICKS(5));   // ~2.8 мс на перезавантаження PROM у регістри
    return err;
}

// Прочитати одне 16-бітне слово PROM за індексом 0..7.
// write_read_device = запис команди, повторний старт, читання — один виклик.
static esp_err_t ms5611_read_prom_word(uint8_t index, uint16_t *out) {
    uint8_t cmd = CMD_PROM_BASE + index * 2;    // A0, A2, A4, ... AE
    uint8_t buf[2];
    esp_err_t err = i2c_master_write_read_device(I2C_PORT, MS5611_ADDR,
                                                 &cmd, 1, buf, 2, I2C_TMO);
    if (err != ESP_OK) return err;
    *out = ((uint16_t)buf[0] << 8) | buf[1];    // старший байт першим
    return ESP_OK;
}

// Прочитати весь PROM (8 слів) у g_prom[]. Викликається раз при старті.
static esp_err_t ms5611_read_prom(void) {
    for (uint8_t i = 0; i < 8; i++) {
        esp_err_t err = ms5611_read_prom_word(i, &g_prom[i]);
        if (err != ESP_OK) return err;
    }
    return ESP_OK;
}
