#include "nvs_flash.h"
#include "esp_log.h"
static const char *TAG = "temp_reader";

// Статус деградації — видимий іншим підсистемам
typedef enum {
    SENSOR_OK         = 0,
    SENSOR_DEGRADED   = 1,   // резерв або last-known-good
    SENSOR_FAILED     = 2,   // повна відмова, консервативний режим
} sensor_status_t;

static sensor_status_t s_temp_status = SENSOR_OK;

// Зовнішні API давачів
esp_err_t primary_sensor_read(float *out_c);    // основний (I2C)
esp_err_t backup_sensor_read(float *out_c);     // запасний (ADC)

float read_temperature_degc(void) {
    float temp;

    // Сходинка 1: основний давач
    if (primary_sensor_read(&temp) == ESP_OK) {
        if (s_temp_status != SENSOR_OK) {
            ESP_LOGI(TAG, "primary sensor restored");
        }
        s_temp_status = SENSOR_OK;
        // Оновити last-known-good, але не щоразу — інакше зносимо Flash
        static uint32_t s_lkg_update_tick = 0;
        if (xTaskGetTickCount() - s_lkg_update_tick > pdMS_TO_TICKS(60000)) {
            nvs_set_i32(nvs_h, "temp_lkg", (int32_t)(temp * 100));
            nvs_commit(nvs_h);
            s_lkg_update_tick = xTaskGetTickCount();
        }
        return temp;
    }

    ESP_LOGW(TAG, "primary sensor failed — trying backup");

    // Сходинка 2: запасний давач
    if (backup_sensor_read(&temp) == ESP_OK) {
        s_temp_status = SENSOR_DEGRADED;
        ESP_LOGW(TAG, "DEGRADED: using backup sensor, temp=%.1f C", temp);
        // Позначити деградацію (індикатор, телеметрія)
        gpio_set_level(GPIO_FAULT_LED, 1);
        mqtt_publish("status/sensor", "degraded:backup");
        return temp;
    }

    ESP_LOGE(TAG, "BOTH sensors failed — using last-known-good");

    // Сходинка 3: last-known-good із NVS
    int32_t lkg_raw = 2000;   // дефолт 20.0 °C, якщо в NVS ще нічого не писали
    nvs_get_i32(nvs_h, "temp_lkg", &lkg_raw);

    s_temp_status = SENSOR_FAILED;
    // Консервативний режим — нагрівач лише до 50% потужності
    heating_set_max_power(50);
    gpio_set_level(GPIO_FAULT_LED, 1);
    mqtt_publish("status/sensor", "failed:last-known-good");

    // ЗАБОРОНЕНО повертати дефолт мовчки — це тихий збій
    return lkg_raw / 100.0f;   // завжди з прапорцем, ніколи мовчки
}

sensor_status_t get_temperature_status(void) {
    return s_temp_status;
}
