#include "relay_driver.h"
#include "esp_log.h"
#include <stddef.h>

static const char *TAG = "RELAY_DRIVER";

/**
 * @brief Допоміжна функція переведення логічного стану реле у фізичний рівень GPIO.
 */
static uint32_t get_physical_level(bool active_low, relay_state_t state)
{
    if (active_low) {
        /* Active LOW: ON -> 0 (LOW), OFF -> 1 (HIGH) */
        return (state == RELAY_STATE_ON) ? 0 : 1;
    } else {
        /* Active HIGH: ON -> 1 (HIGH), OFF -> 0 (LOW) */
        return (state == RELAY_STATE_ON) ? 1 : 0;
    }
}

esp_err_t relay_driver_init(relay_handle_t *handle, const relay_config_t *config)
{
    if (handle == NULL || config == NULL) {
        ESP_LOGE(TAG, "Недійсний аргумент: handle або config дорівнює NULL");
        return ESP_ERR_INVALID_ARG;
    }

    if (config->gpio_pin < 0 || config->gpio_pin >= GPIO_NUM_MAX) {
        ESP_LOGE(TAG, "Некоректний номер GPIO: %d", config->gpio_pin);
        return ESP_ERR_INVALID_ARG;
    }

    handle->gpio_pin = config->gpio_pin;
    handle->active_low = config->active_low;
    handle->current_state = config->initial_state;
    handle->is_initialized = false;

    /* Створення м'ютексу FreeRTOS для синхронізації доступу до реле з різних задач */
    handle->lock = xSemaphoreCreateMutex();
    if (handle->lock == NULL) {
        ESP_LOGE(TAG, "Не вдалося створити м'ютекс FreeRTOS для реле");
        return ESP_ERR_NO_MEM;
    }

    /*
     * ОСОБЛИВІСТЬ КЕРУВАННЯ GPIO0 НА ESP-01S:
     * 1. GPIO0 є конфігураційним виводом (strapping pin) ESP8266. Під час скидання та подачі живлення
     *    рівень на GPIO0 повинен бути HIGH (3.3V), щоб мікроконтролер завантажився з SPI Flash,
     *    а не увійшов у режим програмування (UART Download Mode).
     * 2. Модулі ESP-01S Relay v1.0/v4.0 мають активний низький рівень (Active LOW): NPN/PNP транзистор
     *    або оптопара відкриваються при LOW (0V) на GPIO0.
     * 3. Для запобігання короткочасному імпульсу та хибному клацанню котушки реле під час старт-апу,
     *    потрібно встановити фізичний рівень HIGH до переведення виводу в режим виходу (GPIO_MODE_OUTPUT),
     *    а також увімкнути внутрішнє підтягування Pull-Up.
     */
    uint32_t init_level = get_physical_level(handle->active_low, handle->current_state);

    /* Попереднє встановлення рівня на регістрі GPIO перед конфігурацією режиму */
    gpio_set_level(handle->gpio_pin, init_level);

    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << handle->gpio_pin),
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,   /* Гарантуємо високий рівень під час старту */
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE
    };

    esp_err_t err = gpio_config(&io_conf);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка конфігурації GPIO%d: %s", handle->gpio_pin, esp_err_to_name(err));
        vSemaphoreDelete(handle->lock);
        return err;
    }

    /* Додаткове підтвердження безпечного стану виводу */
    gpio_set_level(handle->gpio_pin, init_level);

    handle->is_initialized = true;

    ESP_LOGI(TAG, "Ініціалізацію GPIO%d завершено успішно (Active %s, початковий стан: %s)",
             handle->gpio_pin,
             handle->active_low ? "LOW" : "HIGH",
             (handle->current_state == RELAY_STATE_ON) ? "ON" : "OFF");

    return ESP_OK;
}

esp_err_t relay_driver_set_state(relay_handle_t *handle, relay_state_t state)
{
    if (handle == NULL || !handle->is_initialized) {
        ESP_LOGE(TAG, "Драйвер реле не ініціалізований");
        return ESP_ERR_INVALID_STATE;
    }

    if (xSemaphoreTake(handle->lock, portMAX_DELAY) == pdTRUE) {
        uint32_t level = get_physical_level(handle->active_low, state);
        esp_err_t err = gpio_set_level(handle->gpio_pin, level);

        if (err == ESP_OK) {
            handle->current_state = state;
            ESP_LOGI(TAG, "Стан реле GPIO%d змінено на: %s (фізичний рівень: %d)",
                     handle->gpio_pin,
                     (state == RELAY_STATE_ON) ? "ON" : "OFF",
                     (int)level);
        } else {
            ESP_LOGE(TAG, "Не вдалося встановити рівень GPIO%d: %s", handle->gpio_pin, esp_err_to_name(err));
        }

        xSemaphoreGive(handle->lock);
        return err;
    }

    return ESP_ERR_TIMEOUT;
}

esp_err_t relay_driver_toggle(relay_handle_t *handle)
{
    if (handle == NULL || !handle->is_initialized) {
        return ESP_ERR_INVALID_STATE;
    }

    relay_state_t new_state = (handle->current_state == RELAY_STATE_ON) ? RELAY_STATE_OFF : RELAY_STATE_ON;
    return relay_driver_set_state(handle, new_state);
}

relay_state_t relay_driver_get_state(relay_handle_t *handle)
{
    if (handle == NULL || !handle->is_initialized) {
        return RELAY_STATE_OFF;
    }

    relay_state_t state = RELAY_STATE_OFF;
    if (xSemaphoreTake(handle->lock, portMAX_DELAY) == pdTRUE) {
        state = handle->current_state;
        xSemaphoreGive(handle->lock);
    }

    return state;
}

esp_err_t relay_driver_deinit(relay_handle_t *handle)
{
    if (handle == NULL || !handle->is_initialized) {
        return ESP_ERR_INVALID_STATE;
    }

    if (xSemaphoreTake(handle->lock, portMAX_DELAY) == pdTRUE) {
        /* Безпечне вимкнення реле перед деініціалізацією */
        uint32_t off_level = get_physical_level(handle->active_low, RELAY_STATE_OFF);
        gpio_set_level(handle->gpio_pin, off_level);

        handle->is_initialized = false;
        xSemaphoreGive(handle->lock);

        vSemaphoreDelete(handle->lock);
        handle->lock = NULL;

        ESP_LOGI(TAG, "Драйвер реле GPIO%d успішно деініціалізовано", handle->gpio_pin);
    }

    return ESP_OK;
}
