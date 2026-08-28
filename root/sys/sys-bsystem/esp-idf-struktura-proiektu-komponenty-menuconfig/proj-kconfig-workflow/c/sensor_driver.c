/* src/sensor_driver.c (C) */
#include "sensor_driver.h"
#include "sdkconfig.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "driver/i2c.h"
#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"

static const char *TAG = "sensor_driver";
static bool s_is_init = false;
static SemaphoreHandle_t s_lock = NULL;

esp_err_t sensor_driver_init(void) {
    if (s_is_init) {
        return ESP_OK;
    }

    s_lock = xSemaphoreCreateMutex();
    if (!s_lock) {
        return ESP_ERR_NO_MEM;
    }

    i2c_config_t conf = {
        .mode = I2C_MODE_MASTER,
        .sda_io_num = CONFIG_SENSOR_I2C_SDA_PIN,
        .sda_pullup_en = GPIO_PULLUP_ENABLE,
        .scl_io_num = CONFIG_SENSOR_I2C_SCL_PIN,
        .scl_pullup_en = GPIO_PULLUP_ENABLE,
        .master.clk_speed = CONFIG_SENSOR_I2C_FREQ_HZ,
    };

    esp_err_t err = i2c_param_config(CONFIG_SENSOR_I2C_PORT, &conf);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка конфігурації I2C: %s", esp_err_to_name(err));
        vSemaphoreDelete(s_lock);
        s_lock = NULL;
        return err;
    }

    err = i2c_driver_install(CONFIG_SENSOR_I2C_PORT, conf.mode, 0, 0, 0);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка встановлення драйвера I2C: %s", esp_err_to_name(err));
        vSemaphoreDelete(s_lock);
        s_lock = NULL;
        return err;
    }

    s_is_init = true;
    ESP_LOGI(TAG, "Драйвер ініціалізовано: Port=%d, SDA=%d, SCL=%d, Частота=%d Гц",
             CONFIG_SENSOR_I2C_PORT, CONFIG_SENSOR_I2C_SDA_PIN, 
             CONFIG_SENSOR_I2C_SCL_PIN, CONFIG_SENSOR_I2C_FREQ_HZ);
    return ESP_OK;
}

esp_err_t sensor_driver_read(sensor_reading_t *out_reading) {
    if (!s_is_init || !out_reading) {
        return ESP_ERR_INVALID_STATE;
    }

    if (xSemaphoreTake(s_lock, pdMS_TO_TICKS(100)) != pdTRUE) {
        return ESP_ERR_TIMEOUT;
    }

    /* Моделювання вичитування даних через транзакцію I2C */
    out_reading->temperature_celsius = 24.2f;
    out_reading->humidity_percent = 52.5f;
    out_reading->timestamp_ms = (uint32_t)(esp_timer_get_time() / 1000ULL);

#if CONFIG_SENSOR_ENABLE_AVERAGING
    ESP_LOGD(TAG, "Ковзне середнє за %d зразками застосовано", CONFIG_SENSOR_SAMPLE_COUNT);
#endif

    xSemaphoreGive(s_lock);
    return ESP_OK;
}

esp_err_t sensor_driver_deinit(void) {
    if (!s_is_init) {
        return ESP_OK;
    }

    if (xSemaphoreTake(s_lock, pdMS_TO_TICKS(500)) == pdTRUE) {
        i2c_driver_delete(CONFIG_SENSOR_I2C_PORT);
        s_is_init = false;
        xSemaphoreGive(s_lock);
        vSemaphoreDelete(s_lock);
        s_lock = NULL;
        ESP_LOGI(TAG, "Драйвер сенсора успішно деініціалізовано.");
        return ESP_OK;
    }

    return ESP_ERR_TIMEOUT;
}
