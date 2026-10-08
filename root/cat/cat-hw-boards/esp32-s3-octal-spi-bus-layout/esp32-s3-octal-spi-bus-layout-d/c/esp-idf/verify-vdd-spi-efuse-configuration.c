#include "esp_efuse.h"
#include "esp_efuse_table.h"
#include "esp_log.h"
#include "driver/gpio.h"

static const char *TAG = "POWER_DOMAIN_CHECK";

// Перевірка конфігурації eFuse для домену живлення VDD_SPI
void verify_vdd_spi_efuse_configuration(void) {
    uint32_t force_reg = 0;
    uint32_t tieh_reg = 0;

    // Зчитування стану eFuse бітів контролю VDD_SPI
    esp_efuse_read_field_blob(ESP_EFUSE_VDD_SPI_FORCE, &force_reg, 1);
    esp_efuse_read_field_blob(ESP_EFUSE_VDD_SPI_TIEH, &tieh_reg, 1);

    if (force_reg) {
        ESP_LOGI(TAG, "Домен VDD_SPI зафіксовано через eFuse (GPIO45 ігнорується)");
        if (tieh_reg) {
            ESP_LOGI(TAG, "Конфігурація напруги VDD_SPI: 1.8 В");
        } else {
            ESP_LOGI(TAG, "Конфігурація напруги VDD_SPI: 3.3 В");
        }
    } else {
        ESP_LOGW(TAG, "Напруга VDD_SPI визначається станом strapping-виводу GPIO45 при старті!");
        int gpio45_val = gpio_get_level(GPIO_NUM_45);
        ESP_LOGI(TAG, "Поточний логічний рівень на GPIO45: %d", gpio45_val);
    }
}
