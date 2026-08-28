#include "driver/i2c.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define PCA_ADDR      0x40        // адреса за замовчуванням
#define REG_MODE1     0x00
#define REG_PRESCALE  0xFE
#define REG_LED0_ON_L 0x06        // далі — по 4 регістри на канал

static esp_err_t pca_write(uint8_t reg, uint8_t val) {
  uint8_t buf[2] = { reg, val };
  return i2c_master_write_to_device(I2C_NUM_0, PCA_ADDR, buf, 2, pdMS_TO_TICKS(100));
}

static void pca_set_freq(int hz) {
  // дільник = round(25 МГц / (4096 · f)) − 1; для 50 Гц це 121
  uint8_t prescale = (uint8_t)(25000000.0 / (4096.0 * hz) + 0.5) - 1;
  pca_write(REG_MODE1, 0x10);     // SLEEP: дільник міняють лише зі сплячим генератором
  pca_write(REG_PRESCALE, prescale);
  pca_write(REG_MODE1, 0x00);     // прокинутись
  vTaskDelay(pdMS_TO_TICKS(1));   // ≥500 мкс на розгін генератора
  pca_write(REG_MODE1, 0xA0);     // RESTART + автоінкремент регістрів
}

static void servo_us(uint8_t ch, int us) {
  if (us < 1000) us = 1000;                       // тримаємось безпечних меж SG90
  if (us > 2000) us = 2000;
  uint16_t off = (uint16_t)(us * 4096 / 20000);   // ≈ 4.88 мкс на крок
  uint8_t base = REG_LED0_ON_L + 4 * ch;
  pca_write(base + 0, 0);                         // ON_L  = 0
  pca_write(base + 1, 0);                         // ON_H  = 0
  pca_write(base + 2, off & 0xFF);                // OFF_L
  pca_write(base + 3, off >> 8);                  // OFF_H
}

void app_main(void) {
  i2c_config_t cfg = {
    .mode = I2C_MODE_MASTER,
    .sda_io_num = 21, .scl_io_num = 22,
    .sda_pullup_en = GPIO_PULLUP_ENABLE,
    .scl_pullup_en = GPIO_PULLUP_ENABLE,
    .master.clk_speed = 400000,
  };
  ESP_ERROR_CHECK(i2c_param_config(I2C_NUM_0, &cfg));
  ESP_ERROR_CHECK(i2c_driver_install(I2C_NUM_0, I2C_MODE_MASTER, 0, 0, 0));

  pca_set_freq(50);               // 50 Гц на ВСІ 16 каналів одразу
  servo_us(0, 1500); servo_us(1, 1500); servo_us(2, 1500);   // три серва по нейтралі

  while (1) {                     // махнути каналом 0, решта стоять
    servo_us(0, 1000); vTaskDelay(pdMS_TO_TICKS(800));
    servo_us(0, 2000); vTaskDelay(pdMS_TO_TICKS(800));
  }
}
