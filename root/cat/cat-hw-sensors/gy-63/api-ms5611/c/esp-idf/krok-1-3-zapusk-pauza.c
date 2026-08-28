#include "esp_rom_sys.h"

// Обраний режим згладжування (код OSR: 0,2,4,6,8) і його пауза в мікросекундах.
static uint8_t g_osr_cmd = 8;                // 8 = OSR 4096 (найвища роздільність)

static uint32_t osr_delay_us(void) {
    switch (g_osr_cmd) {
        case 0:  return 600;                 // OSR 256
        case 2:  return 1200;                // OSR 512
        case 4:  return 2300;                // OSR 1024
        case 6:  return 4600;                // OSR 2048
        default: return 9100;                // OSR 4096
    }
}

// Запустити одне перетворення (start_cmd = CMD_CONV_D1 або CMD_CONV_D2),
// витримати паузу за OSR і прочитати 24-бітний результат АЦП.
static esp_err_t ms5611_convert_read(uint8_t start_cmd, uint32_t *out) {
    uint8_t cmd = start_cmd + g_osr_cmd;     // напр. 0x40 + 8 = 0x48 для тиску @OSR4096
    esp_err_t err = i2c_master_write_to_device(I2C_PORT, MS5611_ADDR, &cmd, 1, I2C_TMO);
    if (err != ESP_OK) return err;

    // vTaskDelay округлює до тика планувальника (типово 10 мс) — для 0.6…9 мс
    // це надто грубо, тому коротку паузу відлічуємо точним лічильником.
    esp_rom_delay_us(osr_delay_us() + 500);  // + запас

    uint8_t rd = CMD_ADC_READ, buf[3];       // 0x00
    err = i2c_master_write_read_device(I2C_PORT, MS5611_ADDR, &rd, 1, buf, 3, I2C_TMO);
    if (err != ESP_OK) return err;

    // 24 біти, старший байт першим
    *out = ((uint32_t)buf[0] << 16) | ((uint32_t)buf[1] << 8) | buf[2];

    // нульовий результат = давач не встиг/не відповів як слід
    return (*out != 0) ? ESP_OK : ESP_ERR_INVALID_RESPONSE;
}
