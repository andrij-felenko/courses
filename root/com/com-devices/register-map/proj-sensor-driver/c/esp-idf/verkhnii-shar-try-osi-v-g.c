#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static void mpu_task(void *arg) {
    float ax, ay, az;
    for (;;) {
        if (mpu_read_accel(&ax, &ay, &az) == ESP_OK) {
            // ax, ay, az — у g, можна використовувати
        }
        vTaskDelay(pdMS_TO_TICKS(20));       // віддати процесор іншим задачам
    }
}

void app_main(void) {
    i2c_config_t cfg = {
        .mode = I2C_MODE_MASTER,
        .sda_io_num = 21, .scl_io_num = 22,
        .sda_pullup_en = GPIO_PULLUP_ENABLE, // слабкі внутрішні; на платі — свої
        .scl_pullup_en = GPIO_PULLUP_ENABLE,
        .master.clk_speed = 400000,
    };
    ESP_ERROR_CHECK(i2c_param_config(I2C_PORT, &cfg));
    ESP_ERROR_CHECK(i2c_driver_install(I2C_PORT, cfg.mode, 0, 0, 0));

    if (!mpu_present()) return;              // біда з дротами/адресою
    if (mpu_begin() != ESP_OK) return;       // збій налаштування
    xTaskCreate(mpu_task, "mpu", 4096, NULL, 5, NULL);
}
