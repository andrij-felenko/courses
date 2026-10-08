#include <stdint.h>
#include <stdbool.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"

#define PIN_CAM_PWDN    21
#define PIN_CAM_RESET   22

void ov3640_hardware_power_on(void)
{
    // Налаштування виводів PWDN та RESET як виходів
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << PIN_CAM_PWDN) | (1ULL << PIN_CAM_RESET),
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE
    };
    gpio_config(&io_conf);

    // Крок 1-3: Тримаємо сенсор у режимі PWDN (активний високий) та RESET (активний низький)
    gpio_set_level(PIN_CAM_PWDN, 1);
    gpio_set_level(PIN_CAM_RESET, 0);

    // Пауза для стабілізації джерел живлення DOVDD, AVDD, DVDD та тактування XVCLK
    vTaskDelay(pdMS_TO_TICKS(15));

    // Крок 5: Пробудження сенсора з режиму сну
    gpio_set_level(PIN_CAM_PWDN, 0);
    vTaskDelay(pdMS_TO_TICKS(5));

    // Зняття апаратного скидання
    gpio_set_level(PIN_CAM_RESET, 1);
    vTaskDelay(pdMS_TO_TICKS(20));
}
