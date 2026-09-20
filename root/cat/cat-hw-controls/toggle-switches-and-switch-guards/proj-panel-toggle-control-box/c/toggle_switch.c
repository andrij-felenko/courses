#include "toggle_switch.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "freertos/task.h"
#include <stdlib.h>

static const char *TAG = "TOGGLE_SWITCH";

struct toggle_switch_handle_s {
    toggle_switch_config_t config;
    QueueHandle_t event_queue;
    toggle_switch_state_t current_state;
    esp_timer_handle_t debounce_timer;
};

// Зчитування миттєвого стану з фізичних ліній GPIO
static toggle_switch_state_t read_physical_state(const toggle_switch_config_t *cfg) {
    bool raw_on1 = false;
    bool raw_on2 = false;

    if (cfg->pin_on1 != GPIO_NUM_NC) {
        int level = gpio_get_level(cfg->pin_on1);
        raw_on1 = cfg->active_low ? (level == 0) : (level == 1);
    }

    if (cfg->pin_on2 != GPIO_NUM_NC) {
        int level = gpio_get_level(cfg->pin_on2);
        raw_on2 = cfg->active_low ? (level == 0) : (level == 1);
    }

    if (raw_on1 && raw_on2) {
        return TOGGLE_STATE_INVALID; // Одночасний контакт на обох лініях
    } else if (raw_on1) {
        return TOGGLE_STATE_ON1;
    } else if (raw_on2) {
        return TOGGLE_STATE_ON2;
    } else {
        return TOGGLE_STATE_OFF;
    }
}

// Колбек таймера програмного дебаунсу
static void debounce_timer_callback(void *arg) {
    toggle_switch_handle_t handle = (toggle_switch_handle_t)arg;
    toggle_switch_state_t new_state = read_physical_state(&handle->config);

    if (new_state != handle->current_state) {
        toggle_switch_event_t evt = {
            .previous_state = handle->current_state,
            .current_state = new_state,
            .timestamp_ms = (uint32_t)(esp_timer_get_time() / 1000)
        };

        handle->current_state = new_state;

        if (handle->event_queue) {
            xQueueSendFromISR(handle->event_queue, &evt, NULL);
        }
    }
}

// Обробник переривань ISR з ліній GPIO тумблера
static void IRAM_ATTR gpio_isr_handler(void *arg) {
    toggle_switch_handle_t handle = (toggle_switch_handle_t)arg;
    
    // Перезапуск таймера дебаунсу для фільтрації брязкоту
    if (handle && handle->debounce_timer) {
        esp_timer_stop(handle->debounce_timer);
        esp_timer_start_once(handle->debounce_timer, handle->config.debounce_ms * 1000);
    }
}

esp_err_t toggle_switch_init(const toggle_switch_config_t *config, 
                           QueueHandle_t event_queue, 
                           toggle_switch_handle_t *out_handle) {
    if (!config || !out_handle) {
        return ESP_ERR_INVALID_ARG;
    }

    toggle_switch_handle_t handle = calloc(1, sizeof(struct toggle_switch_handle_s));
    if (!handle) {
        return ESP_ERR_NO_MEM;
    }

    handle->config = *config;
    handle->event_queue = event_queue;
    handle->current_state = TOGGLE_STATE_OFF;

    // Налаштування GPIO для вхідних ліній тумблера
    gpio_config_t io_conf = {
        .mode = GPIO_MODE_INPUT,
        .intr_type = GPIO_INTR_ANYEDGE
    };

    if (config->active_low) {
        io_conf.pull_up_en = GPIO_PULLUP_ENABLE;
        io_conf.pull_down_en = GPIO_PULLDOWN_DISABLE;
    } else {
        io_conf.pull_up_en = GPIO_PULLUP_DISABLE;
        io_conf.pull_down_en = GPIO_PULLDOWN_ENABLE;
    }

    uint64_t pin_mask = 0;
    if (config->pin_on1 != GPIO_NUM_NC) pin_mask |= (1ULL << config->pin_on1);
    if (config->pin_on2 != GPIO_NUM_NC) pin_mask |= (1ULL << config->pin_on2);
    io_conf.pin_bit_mask = pin_mask;

    gpio_config(&io_conf);

    // Створення неблокувального таймера дебаунсу ESP-IDF
    esp_timer_create_args_t timer_args = {
        .callback = &debounce_timer_callback,
        .arg = handle,
        .name = "toggle_debounce"
    };
    esp_timer_create(&timer_args, &handle->debounce_timer);

    // Встановлення ISR обробників
    gpio_install_isr_service(0);
    if (config->pin_on1 != GPIO_NUM_NC) {
        gpio_isr_handler_add(config->pin_on1, gpio_isr_handler, handle);
    }
    if (config->pin_on2 != GPIO_NUM_NC) {
        gpio_isr_handler_add(config->pin_on2, gpio_isr_handler, handle);
    }

    handle->current_state = read_physical_state(config);
    *out_handle = handle;

    ESP_LOGI(TAG, "Драйвер тумблера успішно ініціалізовано.");
    return ESP_OK;
}

toggle_switch_state_t toggle_switch_get_state(toggle_switch_handle_t handle) {
    return handle ? handle->current_state : TOGGLE_STATE_OFF;
}

esp_err_t toggle_switch_deinit(toggle_switch_handle_t handle) {
    if (!handle) return ESP_ERR_INVALID_ARG;

    if (handle->config.pin_on1 != GPIO_NUM_NC) {
        gpio_isr_handler_remove(handle->config.pin_on1);
    }
    if (handle->config.pin_on2 != GPIO_NUM_NC) {
        gpio_isr_handler_remove(handle->config.pin_on2);
    }

    if (handle->debounce_timer) {
        esp_timer_stop(handle->debounce_timer);
        esp_timer_delete(handle->debounce_timer);
    }

    free(handle);
    return ESP_OK;
}
