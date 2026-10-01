/**
 * @file main.c
 * @brief Тестова прошивка C для перевірки апаратного адаптера-програматора ESP-01.
 * 
 * Здійснює ініціалізацію GPIO2 для керування світлодіодом, опитування стану GPIO0
 * та вивід діагностичних повідомлень у послідовний порт UART.
 */

#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"
#include "driver/uart.h"
#include "esp_log.h"

#define BLINK_GPIO       GPIO_NUM_2   // Вбудований світлодіод на ESP-01 (GPIO2)
#define SENSE_GPIO0      GPIO_NUM_0   // Конфігураційний вивід GPIO0

static const char *TAG = "ESP01_TEST";

/**
 * @brief Ініціалізація периферії GPIO та UART
 */
static void init_hardware(void)
{
    // Налаштування GPIO2 на вихід для керування світлодіодом
    gpio_config_t io_conf_out = {
        .pin_bit_mask = (1ULL << BLINK_GPIO),
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE
    };
    gpio_config(&io_conf_out);

    // Налаштування GPIO0 на вхід із внутрішньою підтяжкою для опитування
    gpio_config_t io_conf_in = {
        .pin_bit_mask = (1ULL << SENSE_GPIO0),
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE
    };
    gpio_config(&io_conf_in);

    // Ініціалізація UART0 для виводу діагностичних логів на швидкості 115200 бод
    uart_config_t uart_config = {
        .baud_rate = 115200,
        .data_bits = UART_DATA_8_BITS,
        .parity    = UART_PARITY_DISABLE,
        .stop_bits = UART_STOP_BITS_1,
        .flow_ctrl = UART_HW_FLOWCTRL_DISABLE
    };
    uart_param_config(UART_NUM_0, &uart_config);
    uart_driver_install(UART_NUM_0, 256, 0, 0, NULL, 0);

    ESP_LOGI(TAG, "Ініціалізацію апаратури адаптера ESP-01 завершено успішно.");
}

/**
 * @brief Точка входу в програму (головна задача FreeRTOS)
 */
void app_main(void)
{
    init_hardware();

    uint32_t loop_count = 0;
    bool led_state = false;

    while (1) {
        // Інверсія стану світлодіода (на платах ESP-01 LED активується низьким рівнем LOW)
        led_state = !led_state;
        gpio_set_level(BLINK_GPIO, led_state ? 0 : 1);

        // Опитування стану виводу GPIO0
        int gpio0_level = gpio_get_level(SENSE_GPIO0);

        // Вивід логу перевірки стану адаптера
        ESP_LOGI(TAG, "[Крок %u] Світлодіод GPIO2: %s | Стан GPIO0: %s (%d)",
                 (unsigned int)loop_count++,
                 led_state ? "УВІМК" : "ВИМК",
                 gpio0_level ? "HIGH (3.3V)" : "LOW (GND)",
                 gpio0_level);

        // Затримка 500 мс для миготіння з частотою 1 Гц
        vTaskDelay(pdMS_TO_TICKS(500));
    }
}
