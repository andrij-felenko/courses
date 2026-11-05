#include <stdio.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_system.h"
#include "esp_log.h"
#include "nvs_flash.h"
#include "efuse_flash_security.h"

static const char *TAG = "MAIN_APP";

void app_main(void)
{
    ESP_LOGI(TAG, "Запуск додатка перевірки безпеки та eFuse ESP32-S3...");

    /* Ініціалізація підсистеми NVS (Non-Volatile Storage) */
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_LOGW(TAG, "Очищення NVS через відсутність вільних сторінок або оновлення структури...");
        ESP_ERROR_CHECK(nvs_flash_erase());
        ret = nvs_flash_init();
    }
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Помилка ініціалізації NVS: %s", esp_err_to_name(ret));
    }

    /* Програмний контроль апаратних засобів захисту мікроконтролера */
    efuse_security_status_t sec_status;
    ret = efuse_security_read_status(&sec_status);
    if (ret == ESP_OK) {
        efuse_security_print_summary(&sec_status);
    } else {
        ESP_LOGE(TAG, "Не вдалося зчитати статус апаратної безпеки: %s", esp_err_to_name(ret));
    }

    /* Тестовий вирівняний запис у зашифрований розділ пам'яті "storage" */
    const char *test_partition = "storage";
    uint8_t test_data[FLASH_ENCRYPTION_BLOCK_SIZE] __attribute__((aligned(4)));

    /* Заповнення тестового блоку контрольним шаблоном (32 байти) */
    for (size_t i = 0; i < FLASH_ENCRYPTION_BLOCK_SIZE; i++) {
        test_data[i] = (uint8_t)(0xAA ^ i);
    }

    ESP_LOGI(TAG, "Виконання тестової операції запису зашифрованих даних у Flash...");
    ret = efuse_security_write_encrypted_partition(test_partition, 0, test_data, sizeof(test_data));
    if (ret == ESP_OK) {
        ESP_LOGI(TAG, "Тестовий запис у розділ '%s' виконано успішно.", test_partition);

        /* Контрольне зчитування для валідації цілісності даних */
        uint8_t read_buffer[FLASH_ENCRYPTION_BLOCK_SIZE];
        ret = efuse_security_read_encrypted_partition(test_partition, 0, read_buffer, sizeof(read_buffer));
        if (ret == ESP_OK) {
            if (memcmp(test_data, read_buffer, sizeof(test_data)) == 0) {
                ESP_LOGI(TAG, "Перевірка зчитаного блоку успішна: дані повністю збігаються!");
            } else {
                ESP_LOGW(TAG, "Увага: зчитані дані відрізняються від записаних (можливо, пам'ять зашифрована на льоту або не витерта)");
            }
        }
    } else {
        ESP_LOGE(TAG, "Тестовий запис у Flash завершився з помилкою: %s (0x%x)", esp_err_to_name(ret), ret);
        ESP_LOGW(TAG, "Переконайтеся, що розділ '%s' існує у таблиці розділів partitions.csv", test_partition);
    }

    ESP_LOGI(TAG, "Модуль перевірки eFuse та апаратної безпеки успішно завершив роботу.");
}
