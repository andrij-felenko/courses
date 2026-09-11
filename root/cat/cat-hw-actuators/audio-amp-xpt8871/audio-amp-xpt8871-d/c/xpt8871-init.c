// Драйвер керування XPT8871 мовою C (для ESP-IDF / FreeRTOS на ESP32)
#include <stdio.h>
#include <stdbool.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"

#define XPT8871_SHDN_PIN        GPIO_NUM_4
#define XPT8871_TWU_DELAY_MS    150

typedef struct {
    gpio_num_t pin;
    bool is_active;
} xpt8871_handle_t;

void xpt8871_init(xpt8871_handle_t *dev, gpio_num_t pin) {
    dev->pin = pin;
    dev->is_active = false;

    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << pin),
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE
    };
    gpio_config(&io_conf);

    // За замовчуванням виставляємо високий рівень для повного глушіння
    gpio_set_level(dev->pin, 1);
}

void xpt8871_wake(xpt8871_handle_t *dev) {
    if (dev->is_active) {
        return;
    }

    // Витримуємо паузу twu для повного заряду CBYPASS до VDD / 2
    vTaskDelay(pdMS_TO_TICKS(XPT8871_TWU_DELAY_MS));

    // Опускаємо SHDN у нуль — підсилювач активний без акустичного щиглика
    gpio_set_level(dev->pin, 0);
    dev->is_active = true;
}

void xpt8871_sleep(xpt8871_handle_t *dev) {
    if (!dev->is_active) {
        return;
    }

    // Миттєво глушимо підсилювач перед зупинкою відтворення
    gpio_set_level(dev->pin, 1);
    dev->is_active = false;
}
