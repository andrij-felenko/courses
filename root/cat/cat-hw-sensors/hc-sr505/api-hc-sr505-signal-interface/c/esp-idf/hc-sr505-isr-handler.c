// C реалізація неблокувального драйвера HC-SR505 для ESP-IDF
#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include "driver/gpio.h"
#include "esp_timer.h"

typedef enum {
    HC_SR505_STATE_QUARANTINE,
    HC_SR505_STATE_IDLE,
    HC_SR505_STATE_MOTION_ACTIVE,
    HC_SR505_STATE_LOCKOUT
} hc_sr505_state_t;

typedef struct {
    gpio_num_t gpio_pin;
    hc_sr505_state_t state;
    uint64_t state_entry_time_us;
    volatile bool edge_flag;
    volatile bool current_level;
    void (*on_motion_start)(void);
    void (*on_motion_end)(void);
} hc_sr505_t;

// Обробник зовнішнього переривання EXTI (ISR)
static void IRAM_ATTR hc_sr505_isr_handler(void *arg) {
    hc_sr505_t *dev = (hc_sr505_t *)arg;
    dev->current_level = gpio_get_level(dev->gpio_pin);
    dev->edge_flag = true;
}

// Ініціалізація апаратної периферії та початкового стану
void hc_sr505_init(hc_sr505_t *dev, gpio_num_t pin, void (*on_start)(void), void (*on_end)(void)) {
    dev->gpio_pin = pin;
    dev->state = HC_SR505_STATE_QUARANTINE;
    dev->state_entry_time_us = esp_timer_get_time();
    dev->edge_flag = false;
    dev->current_level = false;
    dev->on_motion_start = on_start;
    dev->on_motion_end = on_end;

    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << pin),
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_ENABLE,
        .intr_type = GPIO_INTR_ANYEDGE
    };
    gpio_config(&io_conf);

    gpio_isr_handler_add(pin, hc_sr505_isr_handler, (void *)dev);
}

// Неблокувальна функція оновлення станів (викликається у головному циклі)
void hc_sr505_process(hc_sr505_t *dev) {
    uint64_t now_us = esp_timer_get_time();

    switch (dev->state) {
        case HC_SR505_STATE_QUARANTINE:
            // Витримка 15-секундного періоду карантину після подачі живлення
            if ((now_us - dev->state_entry_time_us) >= 15000000ULL) {
                if (gpio_get_level(dev->gpio_pin) == 0) {
                    dev->state = HC_SR505_STATE_IDLE;
                    dev->edge_flag = false;
                }
            }
            break;

        case HC_SR505_STATE_IDLE:
            if (dev->edge_flag) {
                dev->edge_flag = false;
                if (dev->current_level == 1) {
                    dev->state = HC_SR505_STATE_MOTION_ACTIVE;
                    dev->state_entry_time_us = now_us;
                    if (dev->on_motion_start) {
                        dev->on_motion_start();
                    }
                }
            }
            break;

        case HC_SR505_STATE_MOTION_ACTIVE:
            if (dev->edge_flag) {
                dev->edge_flag = false;
                if (dev->current_level == 0) {
                    dev->state = HC_SR505_STATE_LOCKOUT;
                    dev->state_entry_time_us = now_us;
                    if (dev->on_motion_end) {
                        dev->on_motion_end();
                    }
                }
            }
            break;

        case HC_SR505_STATE_LOCKOUT:
            // Пауза відновлення піроелемента (2.5 секунди)
            if ((now_us - dev->state_entry_time_us) >= 2500000ULL) {
                dev->state = HC_SR505_STATE_IDLE;
                dev->edge_flag = false;
            }
            break;
    }
}
