#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_pm.h"
#include "esp_log.h"
#include "esp_err.h"

static const char *TAG = "DFS_POWER_MGMT";

// Хендлер обмежувача частоти CPU
static esp_pm_lock_handle_t s_cpu_max_lock;

// Ініціалізація та конфігурація підсистеми Power Management
void setup_power_management(void)
{
    // Структура параметрів динамічного масштабування частоти (DFS)
    esp_pm_config_t pm_config = {
        .max_freq_mhz = 400,        // Максимальна робоча частота HP CPU (МГц)
        .min_freq_mhz = 40,         // Мінімальна частота CPU (XTAL 40 МГц)
        .light_sleep_enable = true, // Автоматичний перехід у Light-sleep при простоях FreeRTOS
    };

    // Застосування конфігурації DFS у драйвері ESP-IDF
    ESP_ERROR_CHECK(esp_pm_configure(&pm_config));

    // Створення обмежувача частоти CPU для захисту обчислювально містких секцій
    ESP_ERROR_CHECK(esp_pm_lock_create(ESP_PM_CPU_FREQ_MAX, 0, "heavy_calc_lock", &s_cpu_max_lock));

    ESP_LOGI(TAG, "Систему DFS та автоматичний Light-sleep успішно налаштовано.");
}

// Виконання критичного обчислювального блоку з фіксацією максимальної частоти
void perform_intensive_computation(void)
{
    ESP_LOGI(TAG, "Захоплення PM lock: підвищення частоти CPU до 400 МГц");
    
    // Фіксація частоти CPU на максимальному рівні 400 МГц
    ESP_ERROR_CHECK(esp_pm_lock_acquire(s_cpu_max_lock));

    // Імітація високопродуктивних розрахунків (векторизоване DSP / аналіз кадру)
    vTaskDelay(pdMS_TO_TICKS(1500));

    ESP_LOGI(TAG, "Звільнення PM lock: повернення до адаптивного режиму DFS");
    
    // Звільнення обмежувача дозволяє DFS знижувати частоту під час простою
    ESP_ERROR_CHECK(esp_pm_lock_release(s_cpu_max_lock));
}

void app_main(void)
{
    setup_power_management();

    while (1) {
        perform_intensive_computation();
        
        // Під час тривалої паузи DFS знижує частоту CPU до 40 МГц,
        // а при відсутності активних задач чип переходить у Light-sleep
        vTaskDelay(pdMS_TO_TICKS(4000));
    }
}
