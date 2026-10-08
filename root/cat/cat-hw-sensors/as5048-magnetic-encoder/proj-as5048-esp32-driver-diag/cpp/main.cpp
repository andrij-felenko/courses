#include <cstdio>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"
#include "nvs_flash.h"
#include "driver/spi_master.h"
#include "driver/gpio.h"
#include "as5048a.hpp"

static const char* TAG = "MAIN";

// Піни підключення AS5048A до ESP32 (SPI2)
constexpr gpio_num_t PIN_NUM_MISO = GPIO_NUM_19;
constexpr gpio_num_t PIN_NUM_MOSI = GPIO_NUM_23;
constexpr gpio_num_t PIN_NUM_CLK  = GPIO_NUM_18;
constexpr gpio_num_t PIN_NUM_CS   = GPIO_NUM_5;

// Структура для передачі контексту у задачу FreeRTOS
struct TaskArgs {
    encoder::AS5048A* encoder_ptr;
};

/**
 * @brief Задача високої частоти для опитування кута через конвеєрний SPI.
 */
void angle_polling_task(void* pvParameters) {
    auto* args = static_cast<TaskArgs*>(pvParameters);
    encoder::AS5048A& encoder = *(args->encoder_ptr);

    TickType_t last_wake_time = xTaskGetTickCount();
    const TickType_t period_ticks = pdMS_TO_TICKS(2); // Опитування кожні 2 мс (500 Гц)

    uint32_t loop_counter = 0;
    uint32_t error_counter = 0;

    ESP_LOGI(TAG, "Запуск задачі опитування кута енкодера (500 Гц)...");

    while (true) {
        float angle_deg = 0.0f;
        if (encoder.read_angle_degrees(angle_deg)) {
            // Успішне зчитування кута
            loop_counter++;
            
            // Кожну секунду (500 ітерацій) виводимо моніторинг
            if (loop_counter % 500 == 0) {
                ESP_LOGI(TAG, "[#%u] Поточний кут: %7.2f deg | Нуль: %u",
                         static_cast<unsigned>(loop_counter), angle_deg, encoder.get_zero_offset());
            }
        } else {
            error_counter++;
            ESP_LOGW(TAG, "Помилка читання кута! Всього помилок: %u", static_cast<unsigned>(error_counter));
            
            // Скидаємо прапорці помилок давача
            encoder::ErrorFlags errs;
            if (encoder.clear_errors(errs)) {
                ESP_LOGW(TAG, "Прапорці помилок: Framing=%d, InvalidCmd=%d, Parity=%d",
                         errs.framing_error, errs.command_invalid, errs.parity_error);
            }
        }

        vTaskDelayUntil(&last_wake_time, period_ticks);
    }
}

/**
 * @brief Задача фонового моніторингу AGC та рівня магнітного поля.
 */
void diagnostics_task(void* pvParameters) {
    auto* args = static_cast<TaskArgs*>(pvParameters);
    encoder::AS5048A& encoder = *(args->encoder_ptr);

    while (true) {
        vTaskDelay(pdMS_TO_TICKS(3000)); // Опитування раз на 3 секунди

        encoder::DiagnosticStatus diag;
        if (encoder.read_diagnostics(diag)) {
            ESP_LOGI(TAG, "=== ДІАГНОСТИКА AS5048A ===");
            ESP_LOGI(TAG, "AGC: %u/255 | OCF: %d | COF: %d", diag.agc, diag.ocf, diag.cof);
            
            if (diag.comp_high) {
                ESP_LOGW(TAG, "УВАГА: Магнітне поле занадто сильне! Магніт заблизько до давача.");
            } else if (diag.comp_low) {
                ESP_LOGW(TAG, "УВАГА: Магнітне поле заслабке! Перевірте відстань до магніту.");
            } else {
                ESP_LOGI(TAG, "Стан магнітного поля: Оптимальний.");
            }
        }
    }
}

extern "C" void app_main() {
    ESP_LOGI(TAG, "Старт системи керування рухом. Ініціалізація NVS...");

    // Ініціалізація NVS (Необхідна для збереження калібрування)
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK(ret);

    // Ініціалізація шини SPI
    spi_bus_config_t buscfg = {};
    buscfg.miso_io_num = PIN_NUM_MISO;
    buscfg.mosi_io_num = PIN_NUM_MOSI;
    buscfg.sclk_io_num = PIN_NUM_CLK;
    buscfg.quadwp_io_num = -1;
    buscfg.quadhd_io_num = -1;
    buscfg.max_transfer_sz = 32;

    ret = spi_bus_initialize(SPI2_HOST, &buscfg, SPI_DMA_CH_AUTO);
    ESP_ERROR_CHECK(ret);
    ESP_LOGI(TAG, "Шина SPI2 успішно ініціалізована");

    // Створення об'єкта енкодера
    static encoder::AS5048A encoder_inst(SPI2_HOST, PIN_NUM_CS);
    ESP_ERROR_CHECK(encoder_inst.begin());

    // Проведення тестового калібрування нуля при старті (якщо потрібно)
    // encoder_inst.calibrate_zero_position();

    static TaskArgs task_args = { &encoder_inst };

    // Створення задачі FreeRTOS для конвеєрного читання кута на ядрі 1
    xTaskCreatePinnedToCore(
        angle_polling_task,
        "angle_polling",
        4096,
        &task_args,
        configMAX_PRIORITIES - 1, // Високий пріоритет
        nullptr,
        1
    );

    // Створення задачі фонового моніторингу діагностики на ядрі 0
    xTaskCreatePinnedToCore(
        diagnostics_task,
        "diag_task",
        3072,
        &task_args,
        tskIDLE_PRIORITY + 2,
        nullptr,
        0
    );
}
