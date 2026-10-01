/**
 * @file main.c
 * @brief Точка входу в програму (app_main) для плати ESP32-S3-Zero.
 *
 * Демонструє ініціалізацію нативного USB CDC (Type-C), світлодіода WS2812B через RMT
 * та ретрансляцію даних між бездротовою мережею (Wi-Fi/BLE) та USB-портом.
 */

#include <stdio.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_system.h"
#include "esp_log.h"
#include "esp_chip_info.h"
#include "esp_flash.h"
#include "nvs_flash.h"

// Зовнішні оголошення функцій модулів периферії проєкту

// Модуль WS2812B RMT індикації
typedef enum {
    WS2812_STATUS_BOOT = 0,
    WS2812_STATUS_IDLE,
    WS2812_STATUS_DATA_TX_RX,
    WS2812_STATUS_WIRELESS_ACTIVE,
    WS2812_STATUS_ERROR
} ws2812_status_t;

esp_err_t ws2812_rmt_init(int gpio_num);
esp_err_t ws2812_set_status(ws2812_status_t status);

// Модуль нативного USB CDC
esp_err_t usb_cdc_init(void);
bool usb_cdc_is_connected(void);

// Модуль ретрансляції бездротової мережі
esp_err_t net_relay_init(void);
void net_relay_task(void *pvParameters);
bool net_relay_is_client_connected(void);

static const char *TAG = "MAIN_APP";

#define BOARD_WS2812_GPIO  21  // Пін адресованого RGB-світлодіода на платі ESP32-S3-Zero

/**
 * @brief Ініціалізація енергонезалежної пам'яті NVS (необхідна для роботи Wi-Fi та BLE)
 */
static esp_err_t init_nvs(void)
{
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_LOGW(TAG, "Очищення NVS через відсутність вільних сторінок або зміну версії...");
        ESP_ERROR_CHECK(nvs_flash_erase());
        ret = nvs_flash_init();
    }
    return ret;
}

/**
 * @brief Виведення діагностичної інформації про контролер ESP32-S3-Zero
 */
static void print_chip_info(void)
{
    esp_chip_info_t chip_info;
    uint32_t flash_size = 0;
    
    esp_chip_info(&chip_info);
    ESP_LOGI(TAG, "--- ESP32-S3-Zero Система завантажена ---");
    ESP_LOGI(TAG, "Ядра ЦП: %d, Ревізія silicon: %d", chip_info.cores, chip_info.revision);
    ESP_LOGI(TAG, "Підтримка Wi-Fi/BT: %s%s",
             (chip_info.features & CHIP_FEATURE_WIFI_BGN) ? "Wi-Fi 802.11b/g/n " : "",
             (chip_info.features & CHIP_FEATURE_BLE) ? "Bluetooth LE" : "");

    if (esp_flash_get_size(NULL, &flash_size) == ESP_OK) {
        ESP_LOGI(TAG, "Обсяг SPI Flash пам'яті: %lu МБ", (unsigned long)(flash_size / (1024 * 1024)));
    }
    ESP_LOGI(TAG, "Вільна операційна пам'ять (Free Heap): %lu байт", (unsigned long)esp_get_free_heap_size());
}

/**
 * @brief Головна функція програми app_main (точка входу ESP-IDF)
 */
void app_main(void)
{
    ESP_LOGI(TAG, "Запуск ініціалізації периферії ESP32-S3-Zero...");

    // 1. Ініціалізація NVS пам'яті
    ESP_ERROR_CHECK(init_nvs());

    // 2. Ініціалізація індикатора WS2812B через модуль RMT (GPIO 21)
    if (ws2812_rmt_init(BOARD_WS2812_GPIO) == ESP_OK) {
        ws2812_set_status(WS2812_STATUS_BOOT);
        ESP_LOGI(TAG, "Індикатор WS2812B (RMT, GPIO %d) успішно ініціалізовано", BOARD_WS2812_GPIO);
    } else {
        ESP_LOGE(TAG, "Помилка ініціалізації індикатора WS2812B");
    }

    // 3. Друкуємо параметри системи
    print_chip_info();

    // 4. Ініціалізація нативного драйвера USB CDC через порт Type-C (GPIO19/20)
    esp_err_t usb_res = usb_cdc_init();
    if (usb_res != ESP_OK) {
        ESP_LOGE(TAG, "Помилка ініціалізації драйвера USB CDC: %s", esp_err_to_name(usb_res));
        ws2812_set_status(WS2812_STATUS_ERROR);
    } else {
        ESP_LOGI(TAG, "Нативний USB CDC порт Type-C готовий до обміну даними");
    }

    // 5. Ініціалізація бездротових мережевих інтерфейсів (Wi-Fi AP та BLE)
    esp_err_t net_res = net_relay_init();
    if (net_res != ESP_OK) {
        ESP_LOGE(TAG, "Помилка ініціалізації мережевого ретранслятора: %s", esp_err_to_name(net_res));
        ws2812_set_status(WS2812_STATUS_ERROR);
    } else {
        ESP_LOGI(TAG, "Мережевий ретранслятор успішно конфігуровано");
    }

    // 6. Створення фонової задачі FreeRTOS для обробки ретрансляції даних USB <-> Net
    BaseType_t task_created = xTaskCreatePinnedToCore(
        net_relay_task,
        "net_usb_relay",
        4096,
        NULL,
        5,        // Пріоритет задачі
        NULL,
        1         // Запуск на ядрі 1 для збереження реактивності
    );

    if (task_created != pdPASS) {
        ESP_LOGE(TAG, "Не вдалося створити задачу ретрансляції net_usb_relay");
        ws2812_set_status(WS2812_STATUS_ERROR);
    } else {
        ESP_LOGI(TAG, "Задачу ретрансляції даних запущено у фоновому режимі");
        ws2812_set_status(WS2812_STATUS_IDLE);
    }

    // 7. Головний моніторинговий цикл контролера
    while (1) {
        vTaskDelay(pdMS_TO_TICKS(2000));

        // Моніторинг стану підключень та виведення статусу
        bool client_active = net_relay_is_client_connected();
        bool usb_active = usb_cdc_is_connected();

        ESP_LOGD(TAG, "Стан системи: USB CDC=%s | Бездротовий клієнт=%s | Free Heap=%lu байт",
                 usb_active ? "ПІДКЛЮЧЕНО" : "ОЧІКУВАННЯ",
                 client_active ? "АКТИВНИЙ" : "НЕМАЄ",
                 (unsigned long)esp_get_free_heap_size());

        // Динамічна зміна кольору світлодіода за відсутності активного трафіку
        if (!client_active && usb_active) {
            ws2812_set_status(WS2812_STATUS_IDLE);
        } else if (client_active) {
            ws2812_set_status(WS2812_STATUS_WIRELESS_ACTIVE);
        }
    }
}
