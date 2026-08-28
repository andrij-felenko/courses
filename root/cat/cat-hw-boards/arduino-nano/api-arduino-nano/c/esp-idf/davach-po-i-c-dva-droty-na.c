#include "driver/i2c.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define ADDR    0x76            // адреса давача (з даташита)
#define REG_ID  0xD0            // регістр «хто ти»
#define REG_OUT 0xF7            // старший байт виміру
static const char *TAG = "i2c";

// прочитати n байтів від регістра reg у buf; ESP_OK — успіх
static esp_err_t i2c_read(uint8_t reg, uint8_t *buf, size_t n) {
    // write_read = «назвати регістр → ПОВТОРНИЙ СТАРТ → читати», без stop усередині
    return i2c_master_write_read_device(I2C_NUM_0, ADDR, &reg, 1, buf, n,
                                        pdMS_TO_TICKS(100));
}

void app_main(void) {
    const i2c_config_t cfg = {
        .mode = I2C_MODE_MASTER,
        .sda_io_num = 21, .scl_io_num = 22,     // виводи обираємо самі, вони не жорсткі
        .sda_pullup_en = GPIO_PULLUP_ENABLE,     // слабка внутрішня підтяжка
        .scl_pullup_en = GPIO_PULLUP_ENABLE,
        .master.clk_speed = 100000,
    };
    ESP_ERROR_CHECK(i2c_param_config(I2C_NUM_0, &cfg));
    ESP_ERROR_CHECK(i2c_driver_install(I2C_NUM_0, I2C_MODE_MASTER, 0, 0, 0));

    uint8_t id = 0;
    if (i2c_read(REG_ID, &id, 1) == ESP_OK) ESP_LOGI(TAG, "ID = %02X", id);
    else                                    ESP_LOGE(TAG, "немає відповіді");

    while (1) {
        uint8_t raw[2];
        if (i2c_read(REG_OUT, raw, 2) == ESP_OK)
            ESP_LOGI(TAG, "%d", (raw[0] << 8) | raw[1]);   // старший байт першим
        vTaskDelay(pdMS_TO_TICKS(500));
    }
}
