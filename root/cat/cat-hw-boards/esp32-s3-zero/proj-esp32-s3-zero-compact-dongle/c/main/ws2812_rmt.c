/**
 * @file ws2812_rmt.c
 * @brief Налаштування модуля RMT та формування точних часових імпульсів для керування адресованим RGB-світлодіодом WS2812B.
 *
 * Світлодіод WS2812B вимагає точних імпульсів наносекундного діапазону:
 *  - Логічний '0': T0H ~ 350 нс, T0L ~ 800 нс
 *  - Логічний '1': T1H ~ 800 нс, T1L ~ 450 нс
 *  - Сигнал скидання (RESET): тривала низька пауза > 50 мкс
 * Периферійний модуль RMT (Remote Control) ESP32-S3 генерує ці часові інтервали
 * без залучення ядра процесора.
 */

#include <stdio.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/semphr.h"
#include "driver/gpio.h"
#include "driver/rmt.h"
#include "esp_log.h"
#include "esp_err.h"

static const char *TAG = "WS2812_RMT";

#define RMT_TX_CHANNEL       RMT_CHANNEL_0
#define RMT_CLK_DIV          4        // Тактування 80 МГц / 4 = 20 МГц (1 тик = 50 нс)

// Розрахунок кількості тиків RMT для WS2812B (1 тик = 50 нс):
// T0H: 350 нс -> 7 тиків,  T0L: 800 нс -> 16 тиків
// T1H: 800 нс -> 16 тиків, T1L: 450 нс -> 9 тиків
#define WS2812_T0H_TICKS     7
#define WS2812_T0L_TICKS     16
#define WS2812_T1H_TICKS     16
#define WS2812_T1L_TICKS     9

typedef enum {
    WS2812_STATUS_BOOT = 0,
    WS2812_STATUS_IDLE,
    WS2812_STATUS_DATA_TX_RX,
    WS2812_STATUS_WIRELESS_ACTIVE,
    WS2812_STATUS_ERROR
} ws2812_status_t;

static bool s_rmt_initialized = false;
static SemaphoreHandle_t s_ws2812_mutex = NULL;

/**
 * @brief Перетворення кольорів у формат RMT імпульсів WS2812B
 * Світлодіод WS2812B очікує послідовність у порядку Green - Red - Blue (GRB), MSB спочатку.
 */
static void build_ws2812_items(uint8_t red, uint8_t green, uint8_t blue, rmt_item32_t *items)
{
    // Компонування кольорів у форматі GRB
    uint32_t grb_color = ((uint32_t)green << 16) | ((uint32_t)red << 8) | (uint32_t)blue;

    for (int bit = 0; bit < 24; bit++) {
        // Отримання значення біта (від старшого 23 до молодшого 0)
        bool bit_is_one = (grb_color >> (23 - bit)) & 0x01;

        if (bit_is_one) {
            // Імпульс для біта '1'
            items[bit] = (rmt_item32_t){
                {{{ WS2812_T1H_TICKS, 1, WS2812_T1L_TICKS, 0 }}}
            };
        } else {
            // Імпульс для біта '0'
            items[bit] = (rmt_item32_t){
                {{{ WS2812_T0H_TICKS, 1, WS2812_T0L_TICKS, 0 }}}
            };
        }
    }
}

/**
 * @brief Ініціалізація RMT каналу для виведення на пін WS2812B
 * @param gpio_num Номер GPIO піна (для ESP32-S3-Zero це GPIO 21)
 */
esp_err_t ws2812_rmt_init(gpio_num_t gpio_num)
{
    if (s_rmt_initialized) {
        return ESP_OK;
    }

    s_ws2812_mutex = xSemaphoreCreateMutex();
    if (s_ws2812_mutex == NULL) {
        ESP_LOGE(TAG, "Не вдалося створити м'ютекс захисту WS2812");
        return ESP_ERR_NO_MEM;
    }

    // Конфігурація периферійного каналу RMT для передачі
    rmt_config_t config = RMT_DEFAULT_CONFIG_TX(gpio_num, RMT_TX_CHANNEL);
    config.clk_div = RMT_CLK_DIV;

    esp_err_t err = rmt_config(&config);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Конфігурація RMT завершилася помилкою: %s", esp_err_to_name(err));
        return err;
    }

    err = rmt_driver_install(RMT_TX_CHANNEL, 0, 0);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Встановлення драйвера RMT завершилося помилкою: %s", esp_err_to_name(err));
        return err;
    }

    s_rmt_initialized = true;
    ESP_LOGI(TAG, "Модуль RMT успішно конфігуровано для WS2812B на GPIO %d", gpio_num);
    return ESP_OK;
}

/**
 * @brief Встановлення довільного RGB кольору на світлодіоді
 */
esp_err_t ws2812_set_rgb(uint8_t red, uint8_t green, uint8_t blue)
{
    if (!s_rmt_initialized) {
        return ESP_ERR_INVALID_STATE;
    }

    rmt_item32_t items[24];
    build_ws2812_items(red, green, blue, items);

    if (xSemaphoreTake(s_ws2812_mutex, pdMS_TO_TICKS(100)) == pdTRUE) {
        esp_err_t err = rmt_write_items(RMT_TX_CHANNEL, items, 24, true);
        rmt_wait_tx_done(RMT_TX_CHANNEL, pdMS_TO_TICKS(50));
        xSemaphoreGive(s_ws2812_mutex);
        return err;
    }

    return ESP_ERR_TIMEOUT;
}

/**
 * @brief Відображення попередньо визначеного статусу пристрою за допомогою кольору
 */
esp_err_t ws2812_set_status(ws2812_status_t status)
{
    switch (status) {
        case WS2812_STATUS_BOOT:
            // Фіолетовий (Завантаження)
            return ws2812_set_rgb(32, 0, 32);

        case WS2812_STATUS_IDLE:
            // Зелений (Готовий / USB підключено)
            return ws2812_set_rgb(0, 32, 0);

        case WS2812_STATUS_DATA_TX_RX:
            // Жовтий/Оранжевий (Активна ретрансляція даних)
            return ws2812_set_rgb(48, 32, 0);

        case WS2812_STATUS_WIRELESS_ACTIVE:
            // Синій (Бездротове підключення активне)
            return ws2812_set_rgb(0, 0, 48);

        case WS2812_STATUS_ERROR:
            // Червоний (Помилка)
            return ws2812_set_rgb(48, 0, 0);

        default:
            return ws2812_set_rgb(0, 0, 0);
    }
}
