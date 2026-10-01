#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_system.h"
#include "esp_chip_info.h"
#include "esp_flash.h"
#include "esp_log.h"
#include "board_diag.h"

static const char *TAG = "MAIN_APP";

void app_main(void)
{
    // Ініціалізація консольного виводу через USB CDC/JTAG
    esp_err_t ret = board_diag_init_usb_cdc();
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Старт перервано через помилку CDC/JTAG");
    }

    vTaskDelay(pdMS_TO_TICKS(1000));

    ESP_LOGI(TAG, "Старт системи первинної діагностики модулів ESP32-S3...");

    // Отримання інформації про чіп ESP32-S3
    esp_chip_info_t chip_info;
    esp_chip_info(&chip_info);

    printf("\n--- АПАРАТНА ІНФОРМАЦІЯ ЧІПА ESP32-S3 ---\n");
    printf("Модель чіпа: ESP32-S3 (ревізія %d)\n", chip_info.revision);
    printf("Кількість ядер CPU: %d\n", chip_info.cores);
    printf("Підтримка Wi-Fi / BLE: %s / %s\n",
           (chip_info.features & CHIP_FEATURE_WIFI_BGN) ? "Так" : "Ні",
           (chip_info.features & CHIP_FEATURE_BLE) ? "Так" : "Ні");

    uint32_t flash_size = 0;
    if (esp_flash_get_size(NULL, &flash_size) == ESP_OK) {
        printf("Обсяг Flash-пам'яті: %lu МБ\n", (unsigned long)(flash_size / (1024 * 1024)));
    }
    printf("----------------------------------------\n");

    // Зчитування та виведення статусу strapping pins
    board_strap_status_t strap_status;
    ret = board_diag_read_strapping_pins(&strap_status);
    if (ret == ESP_OK) {
        board_diag_print_report(&strap_status);
    } else {
        ESP_LOGE(TAG, "Не вдалося зчитати стан strapping pins");
    }

    // Тестування сигнального зв'язку між GPIO виводами
    ret = board_diag_test_gpio_loopback(DIAG_TEST_GPIO_OUT, DIAG_TEST_GPIO_IN);
    if (ret == ESP_OK) {
        ESP_LOGI(TAG, "Діагностика апаратного забезпечення плати завершена успішно.");
    } else {
        ESP_LOGW(TAG, "Діагностику завершено із зауваженнями до GPIO loopback.");
    }

    // Головний цикл моніторингу
    while (1) {
        vTaskDelay(pdMS_TO_TICKS(5000));
        ESP_LOGI(TAG, "Моніторинг плати активний. Вільна пам'ять Heap: %lu байтів",
                 (unsigned long)esp_get_free_heap_size());
    }
}
