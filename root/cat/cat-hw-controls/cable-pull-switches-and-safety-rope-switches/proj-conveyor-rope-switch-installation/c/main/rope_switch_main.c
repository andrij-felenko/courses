#include <stdio.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/queue.h"
#include "driver/gpio.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "rope_switch.h"

static const char *TAG = "ROPE_SWITCH";

static QueueHandle_t s_gpio_evt_queue = NULL;
static rope_switch_config_t s_config;
static volatile rope_switch_state_t s_current_state = ROPE_SWITCH_STATE_TRIPPED;

static void IRAM_ATTR gpio_isr_handler(void *arg) {
    uint32_t gpio_num = (uint32_t) arg;
    rope_switch_evt_t evt;
    evt.pin = (gpio_num_t)gpio_num;
    evt.timestamp_ms = (uint32_t)(esp_timer_get_time() / 1000);
    evt.level = gpio_get_level(evt.pin);
    xQueueSendFromISR(s_gpio_evt_queue, &evt, NULL);
}

const char* rope_switch_state_to_str(rope_switch_state_t state) {
    switch (state) {
        case ROPE_SWITCH_STATE_OK:
            return "НОРМА (ОК)";
        case ROPE_SWITCH_STATE_TRIPPED:
            return "АВАРІЯ: Трос натягнуто/обірвано";
        case ROPE_SWITCH_STATE_FAULT_DISCREPANCY:
            return "ПОМИЛКА: Розсинхронізація каналів";
        case ROPE_SWITCH_STATE_WAIT_RESET:
            return "ОЧІКУВАННЯ СКИДУ (Reset)";
        default:
            return "НЕВІДОМИЙ СТАН";
    }
}

rope_switch_state_t rope_switch_get_state(void) {
    return s_current_state;
}

static void update_status_led(rope_switch_state_t state) {
    if (s_config.status_led_pin == GPIO_NUM_NC) return;
    
    switch (state) {
        case ROPE_SWITCH_STATE_OK:
            gpio_set_level(s_config.status_led_pin, 1);
            break;
        case ROPE_SWITCH_STATE_WAIT_RESET:
            break;
        default:
            gpio_set_level(s_config.status_led_pin, 0);
            break;
    }
}

static void set_state(rope_switch_state_t new_state) {
    if (s_current_state != new_state) {
        ESP_LOGI(TAG, "Зміна стану: [%s] -> [%s]", 
                 rope_switch_state_to_str(s_current_state), 
                 rope_switch_state_to_str(new_state));
        s_current_state = new_state;
        update_status_led(new_state);
    }
}

static void rope_switch_task(void *arg) {
    rope_switch_evt_t evt;
    uint32_t ch1_change_time = 0;
    uint32_t ch2_change_time = 0;
    bool ch1_active_change = false;
    bool ch2_active_change = false;

    while (1) {
        if (xQueueReceive(s_gpio_evt_queue, &evt, pdMS_TO_TICKS(50))) {
            vTaskDelay(pdMS_TO_TICKS(s_config.debounce_ms));
            
            int ch1_val = gpio_get_level(s_config.ch1_pin);
            int ch2_val = gpio_get_level(s_config.ch2_pin);
            uint32_t now = (uint32_t)(esp_timer_get_time() / 1000);

            if (evt.pin == s_config.ch1_pin) {
                ch1_change_time = now;
                ch1_active_change = true;
            } else if (evt.pin == s_config.ch2_pin) {
                ch2_change_time = now;
                ch2_active_change = true;
            }

            if (ch1_val == 1 && ch2_val == 1) {
                if (s_current_state != ROPE_SWITCH_STATE_FAULT_DISCREPANCY) {
                    set_state(ROPE_SWITCH_STATE_TRIPPED);
                }
                ch1_active_change = false;
                ch2_active_change = false;
            } else if (ch1_val == 0 && ch2_val == 0) {
                if (s_current_state == ROPE_SWITCH_STATE_TRIPPED) {
                    set_state(ROPE_SWITCH_STATE_WAIT_RESET);
                }
                ch1_active_change = false;
                ch2_active_change = false;
            }
        }

        uint32_t current_time = (uint32_t)(esp_timer_get_time() / 1000);
        int ch1_now = gpio_get_level(s_config.ch1_pin);
        int ch2_now = gpio_get_level(s_config.ch2_pin);

        if (ch1_now != ch2_now) {
            uint32_t start_time = ch1_active_change ? ch1_change_time : ch2_change_time;
            if (start_time > 0 && (current_time - start_time) > s_config.discrepancy_ms) {
                ESP_LOGE(TAG, "Виявлено розбіжність каналів! CH1=%d, CH2=%d більше %lu мс",
                         ch1_now, ch2_now, s_config.discrepancy_ms);
                set_state(ROPE_SWITCH_STATE_FAULT_DISCREPANCY);
            }
        }

        int reset_btn = gpio_get_level(s_config.reset_btn_pin);
        if (reset_btn == 0) {
            vTaskDelay(pdMS_TO_TICKS(s_config.debounce_ms));
            if (gpio_get_level(s_config.reset_btn_pin) == 0) {
                if (ch1_now == 0 && ch2_now == 0) {
                    ESP_LOGI(TAG, "Отримано сигнал квитування (Reset). Відновлення роботи.");
                    ch1_active_change = false;
                    ch2_active_change = false;
                    set_state(ROPE_SWITCH_STATE_OK);
                } else {
                    ESP_LOGW(TAG, "Спроба скиду невдала: шлейф не відновлено (CH1=%d, CH2=%d)",
                             ch1_now, ch2_now);
                }
            }
        }

        if (s_current_state == ROPE_SWITCH_STATE_WAIT_RESET && s_config.status_led_pin != GPIO_NUM_NC) {
            static bool toggle = false;
            toggle = !toggle;
            gpio_set_level(s_config.status_led_pin, toggle ? 1 : 0);
        }
    }
}

esp_err_t rope_switch_init(const rope_switch_config_t *config) {
    if (config == NULL) return ESP_ERR_INVALID_ARG;
    s_config = *config;

    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << config->ch1_pin) | (1ULL << config->ch2_pin),
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_ANYEDGE
    };
    gpio_config(&io_conf);

    io_conf.pin_bit_mask = (1ULL << config->reset_btn_pin);
    io_conf.mode = GPIO_MODE_INPUT;
    io_conf.pull_up_en = GPIO_PULLUP_ENABLE;
    io_conf.pull_down_en = GPIO_PULLDOWN_DISABLE;
    io_conf.intr_type = GPIO_INTR_DISABLE;
    gpio_config(&io_conf);

    if (config->status_led_pin != GPIO_NUM_NC) {
        io_conf.pin_bit_mask = (1ULL << config->status_led_pin);
        io_conf.mode = GPIO_MODE_OUTPUT;
        io_conf.pull_up_en = GPIO_PULLUP_DISABLE;
        io_conf.pull_down_en = GPIO_PULLDOWN_DISABLE;
        io_conf.intr_type = GPIO_INTR_DISABLE;
        gpio_config(&io_conf);
    }

    s_gpio_evt_queue = xQueueCreate(10, sizeof(rope_switch_evt_t));
    if (s_gpio_evt_queue == NULL) {
        ESP_LOGE(TAG, "Не вдалося створити чергу подій GPIO");
        return ESP_ERR_NO_MEM;
    }

    xTaskCreate(rope_switch_task, "rope_switch_task", 3072, NULL, 10, NULL);

    gpio_install_isr_service(0);
    gpio_isr_handler_add(config->ch1_pin, gpio_isr_handler, (void*) config->ch1_pin);
    gpio_isr_handler_add(config->ch2_pin, gpio_isr_handler, (void*) config->ch2_pin);

    int c1 = gpio_get_level(config->ch1_pin);
    int c2 = gpio_get_level(config->ch2_pin);
    if (c1 == 0 && c2 == 0) {
        set_state(ROPE_SWITCH_STATE_WAIT_RESET);
    } else {
        set_state(ROPE_SWITCH_STATE_TRIPPED);
    }

    ESP_LOGI(TAG, "Драйвер тросового вимикача успішно ініціалізовано.");
    return ESP_OK;
}

void app_main(void) {
    ESP_LOGI(TAG, "Запуск системи моніторингу тросового вимикача безпеки...");

    rope_switch_config_t config = {
        .ch1_pin = GPIO_NUM_18,
        .ch2_pin = GPIO_NUM_19,
        .reset_btn_pin = GPIO_NUM_21,
        .status_led_pin = GPIO_NUM_2,
        .discrepancy_ms = 100,
        .debounce_ms = 20
    };

    ESP_ERROR_CHECK(rope_switch_init(&config));

    while (1) {
        rope_switch_state_t current = rope_switch_get_state();
        ESP_LOGI(TAG, "Стан системи: %s", rope_switch_state_to_str(current));
        vTaskDelay(pdMS_TO_TICKS(2000));
    }
}
