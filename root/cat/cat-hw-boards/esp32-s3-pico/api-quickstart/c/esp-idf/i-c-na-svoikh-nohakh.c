#include "driver/i2c.h"
#include "esp_log.h"

static const char *TAG = "i2c";

void app_main(void) {
  i2c_config_t cfg = {
    .mode = I2C_MODE_MASTER,
    .sda_io_num = 8,                    // SDA=GPIO8, SCL=GPIO9 — свої ноги
    .scl_io_num = 9,
    .sda_pullup_en = GPIO_PULLUP_ENABLE, // слабка внутрішня; зовнішня однаково потрібна
    .scl_pullup_en = GPIO_PULLUP_ENABLE,
    .master.clk_speed = 400000,          // 400 кГц (fast mode)
  };
  i2c_param_config(I2C_NUM_0, &cfg);
  i2c_driver_install(I2C_NUM_0, cfg.mode, 0, 0, 0);

  i2c_cmd_handle_t cmd = i2c_cmd_link_create();   // чи є хтось за адресою 0x76?
  i2c_master_start(cmd);
  i2c_master_write_byte(cmd, (0x76 << 1) | I2C_MASTER_WRITE, true);
  i2c_master_stop(cmd);
  esp_err_t err = i2c_master_cmd_begin(I2C_NUM_0, cmd, pdMS_TO_TICKS(100));
  i2c_cmd_link_delete(cmd);

  if (err == ESP_OK) ESP_LOGI(TAG, "BMP280 відповідає");
  else               ESP_LOGW(TAG, "тиша на шині: перевір ноги, живлення й підтяжки");
}
