#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/queue.h"
#include "esp_log.h"
#include "thumbwheel_74hc165.h"

static const char *TAG = "MAIN_APP";

// Потокобезпечна черга FreeRTOS для передачі зчитаних уставок BCD
static QueueHandle_t s_bcd_queue = NULL;

/**
 * @brief Фонова задача FreeRTOS для періодичного опитування барабанних перемикачів
 */
static void vThumbwheelPollTask(void *pvParameters)
{
    thumbwheel_data_t data;

    while (1) {
        esp_err_t err = thumbwheel_read(&data);
        if (err == ESP_OK && data.valid) {
            // Передача підтвердженого BCD-кадру до черги
            xQueueSend(s_bcd_queue, &data, 0);
        }

        // Періодичність опитування 20 мс (50 Гц)
        vTaskDelay(pdMS_TO_TICKS(20));
    }
}

void app_main(void)
{
    ESP_LOGI(TAG, "Запуск системи ручного введення на BCD барабанних перемикачах");

    // Створення черги FreeRTOS на 5 елементів
    s_bcd_queue = xQueueCreate(5, sizeof(thumbwheel_data_t));
    if (s_bcd_queue == NULL) {
        ESP_LOGE(TAG, "Не вдалося створити чергу FreeRTOS");
        return;
    }

    // Налаштування конфігурації для 4 декад BCD (каскад із двох 74HC165)
    thumbwheel_config_t config = {
        .spi_host = SPI2_HOST,
        .pin_pl = GPIO_NUM_5,      // Вивід защелкування Parallel Load
        .pin_miso = GPIO_NUM_19,   // Дані з Q7 останнього 74HC165
        .pin_sclk = GPIO_NUM_18,   // Тактовий сигнал SPI
        .num_digits = 4,           // 4 перемикачі (значення 0000..9999)
        .debounce_ms = 10,         // Час стабілізації брязкоту 10 мс
        .active_low = false        // Пряма логіка контактних доріжок
    };

    esp_err_t err = thumbwheel_init(&config);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Сбій ініціалізації драйвера 74HC165");
        return;
    }

    // Створення фонової задачі зчитування з пріоритетом 5
    xTaskCreate(vThumbwheelPollTask, "thumbwheel_poll", 3072, NULL, 5, NULL);

    thumbwheel_data_t received_data;
    uint32_t last_displayed_value = 0xFFFFFFFF;

    // Головний цикл обробки отриманих уставок
    while (1) {
        if (xQueueReceive(s_bcd_queue, &received_data, portMAX_DELAY) == pdTRUE) {
            if (received_data.raw_value != last_displayed_value) {
                last_displayed_value = received_data.raw_value;

                ESP_LOGI(TAG, "Встановлено нову уставку BCD: %04lu (Декади: [%d, %d, %d, %d])",
                         (unsigned long)received_data.raw_value,
                         received_data.digits[3],
                         received_data.digits[2],
                         received_data.digits[1],
                         received_data.digits[0]);
            }
        }
    }
}
