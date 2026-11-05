#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"
#include "i2c_level_shifter.h"

static const char *TAG = "MAIN_APP";

#define SENSOR_I2C_ADDR       0x68  ///< 7-бітний адрес 5-вольтового датчика (наприклад, годинник реального часу DS3231)
#define SENSOR_REG_SECONDS    0x00  ///< Адреса початкового регістра даних
#define SENSOR_REG_CONTROL    0x0E  ///< Адреса регістра конфігурації

// Допоміжна функція переведення з двійково-десяткового коду BCD у двійковий
static inline uint8_t bcd_to_dec(uint8_t val) {
    return (uint8_t)(((val >> 4) * 10) + (val & 0x0F));
}

void app_main(void) {
    ESP_LOGI(TAG, "Запуск вузла зв'язку з 5-вольтовим давачем через MOSFET транслятор BSS138...");

    // Конфігурація шини: виводи GPIO 21 (SDA) та GPIO 22 (SCL), тактування 100 кГц
    i2c_shifter_config_t i2c_bus = {
        .port = I2C_NUM_0,
        .sda_pin = 21,
        .scl_pin = 22,
        .speed_hz = I2C_SPEED_STANDARD_100K,
        .enable_internal_pullup = false, // Використовуємо зовнішні резистори 10 кОм перетворювача рівнів
        .timeout_ms = 50
    };

    esp_err_t err = i2c_shifter_init(&i2c_bus);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Не вдалося ініціалізувати шину I2C: %s", esp_err_to_name(err));
        return;
    }

    // Перевірка готовності 5-вольтового веденого пристрою
    uint8_t ctrl_val = 0;
    err = i2c_shifter_read_reg(&i2c_bus, SENSOR_I2C_ADDR, SENSOR_REG_CONTROL, &ctrl_val, 1);
    if (err == ESP_OK) {
        ESP_LOGI(TAG, "5V пристрій на зв'язку (0x%02X). Регістр керування: 0x%02X",
                 SENSOR_I2C_ADDR, ctrl_val);
    } else {
        ESP_LOGW(TAG, "Пристрій 0x%02X не відповів (перевірте підключення ліній HV/LV та живлення 5 В)",
                 SENSOR_I2C_ADDR);
    }

    // Головний цикл періодичного опитування телеметрії давача
    uint8_t time_raw[3] = {0}; // секунди, хвилини, години
    uint32_t poll_count = 0;

    while (1) {
        err = i2c_shifter_read_reg(&i2c_bus, SENSOR_I2C_ADDR, SENSOR_REG_SECONDS, time_raw, sizeof(time_raw));

        if (err == ESP_OK) {
            uint8_t sec = bcd_to_dec(time_raw[0] & 0x7F);
            uint8_t min = bcd_to_dec(time_raw[1] & 0x7F);
            uint8_t hour = bcd_to_dec(time_raw[2] & 0x3F);

            ESP_LOGI(TAG, "[Транзакція #%u] Час з 5V сенсора: %02d:%02d:%02d",
                     (unsigned)++poll_count, hour, min, sec);
        } else if (err == ESP_ERR_TIMEOUT) {
            ESP_LOGE(TAG, "Тайм-аут шини I2C! Можливе затягування фронтів R_PU або зависання SDA в LOW");
        } else {
            ESP_LOGE(TAG, "Помилка передачі I2C: %s (NACK від 5V сторони)", esp_err_to_name(err));
        }

        vTaskDelay(pdMS_TO_TICKS(1000));
    }

    // Звільнення ресурсів при виході
    i2c_shifter_deinit(i2c_bus.port);
}
