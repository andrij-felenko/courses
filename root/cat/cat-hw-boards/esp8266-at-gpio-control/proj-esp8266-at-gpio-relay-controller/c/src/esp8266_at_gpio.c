#include "esp8266_at_gpio.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>

/**
 * @file esp8266_at_gpio.c
 * @brief Реалізація методів C-драйвера ESP8266 AT GPIO.
 * 
 * Включає неблокуючий парсинг відповідних рядків OK / ERROR з урахуванням таймаутів,
 * форматування команд AT+PINMODE, AT+PINWRITE, AT+PINREAD та алгоритм безпечного
 * керування силовим реле.
 */

static esp8266_gpio_config_t s_config;
static bool s_driver_initialized = false;

/**
 * @brief Внутрішня неблокуюча функція очікування підтвердження OK або ERROR від ESP8266.
 * 
 * @param timeout_ms Максимальний час очікування в мілісекундах.
 * @return ESP8266_GPIO_OK при отриманні "OK\r\n", 
 *         ESP8266_GPIO_ERR_AT_ERROR при "ERROR\r\n", 
 *         ESP8266_GPIO_ERR_TIMEOUT при перевищенні часу.
 */
static esp8266_gpio_err_t wait_for_at_response(uint32_t timeout_ms) {
    if (!s_config.get_ticks_ms || !s_config.rx_buffer) {
        return ESP8266_GPIO_ERR_INVALID_PARAM;
    }

    uint32_t start_time = s_config.get_ticks_ms();

    while ((s_config.get_ticks_ms() - start_time) < timeout_ms) {
        int ok_idx = uart_ring_buffer_find(s_config.rx_buffer, "OK\r\n");
        if (ok_idx >= 0) {
            uart_ring_buffer_skip(s_config.rx_buffer, (uint16_t)(ok_idx + 4));
            return ESP8266_GPIO_OK;
        }

        int err_idx = uart_ring_buffer_find(s_config.rx_buffer, "ERROR\r\n");
        if (err_idx >= 0) {
            uart_ring_buffer_skip(s_config.rx_buffer, (uint16_t)(err_idx + 7));
            return ESP8266_GPIO_ERR_AT_ERROR;
        }

        if (s_config.delay_ms) {
            s_config.delay_ms(1);
        }
    }

    return ESP8266_GPIO_ERR_TIMEOUT;
}

/**
 * @brief Внутрішній метод відправлення AT-команди у послідовний порт та очікування відповіді.
 */
static esp8266_gpio_err_t send_at_cmd_formatted(const char *fmt, ...) {
    char cmd_buf[128];
    va_list args;
    va_start(args, fmt);
    int len = vsnprintf(cmd_buf, sizeof(cmd_buf), fmt, args);
    va_end(args);

    if (len < 0 || len >= (int)sizeof(cmd_buf)) {
        return ESP8266_GPIO_ERR_INVALID_PARAM;
    }

    /* Очищуємо застарілі дані з буфера перед надсиланням нової інструкції */
    uart_ring_buffer_clear(s_config.rx_buffer);

    /* Передаємо рядок AT-команди в послідовний порт */
    uart_tx_string(cmd_buf);

    /* Неблокуюче очікування статусного підтвердження OK/ERROR */
    return wait_for_at_response(s_config.default_timeout_ms);
}

esp8266_gpio_err_t esp8266_gpio_init(const esp8266_gpio_config_t *config) {
    if (!config || !config->rx_buffer || !config->get_ticks_ms || !config->delay_ms) {
        return ESP8266_GPIO_ERR_INVALID_PARAM;
    }

    s_config = *config;

    /*
     * КРОК 1: Затримка стабілізації живлення та strapping pins (GPIO0, GPIO2, GPIO15).
     * При старті модуля ESP8266 вбудований ROM-завантажувач опитує логічні рівні
     * на цих виводах для вибору режиму завантаження (Flash Boot vs UART Download).
     * Апаратна затримка гарантує закінчення процедури скидання чипа.
     */
    if (s_config.boot_stabilization_delay_ms > 0) {
        s_config.delay_ms(s_config.boot_stabilization_delay_ms);
    }

    /*
     * КРОК 2: Синхронізація послідовного порту UART відправкою базової AT інструкції.
     */
    esp8266_gpio_err_t status = ESP8266_GPIO_ERR_UNRESPONSIVE;
    for (int attempt = 0; attempt < 3; attempt++) {
        uart_ring_buffer_clear(s_config.rx_buffer);
        uart_tx_string("AT\r\n");
        if (wait_for_at_response(s_config.default_timeout_ms) == ESP8266_GPIO_OK) {
            status = ESP8266_GPIO_OK;
            break;
        }
        s_config.delay_ms(50);
    }

    if (status != ESP8266_GPIO_OK) {
        return ESP8266_GPIO_ERR_UNRESPONSIVE;
    }

    /*
     * КРОК 3: Вимкнення луни (ATE0) для спрощення парсингу вхідного потоку байтів.
     */
    if (s_config.disable_echo) {
        send_at_cmd_formatted("ATE0\r\n");
    }

    s_driver_initialized = true;
    return ESP8266_GPIO_OK;
}

bool esp8266_gpio_is_strapping_pin(uint8_t pin) {
    return (pin == ESP8266_STRAPPING_PIN_GPIO0 ||
            pin == ESP8266_STRAPPING_PIN_GPIO2 ||
            pin == ESP8266_STRAPPING_PIN_GPIO15);
}

esp8266_gpio_err_t esp8266_gpio_set_mode(uint8_t pin, esp8266_gpio_mode_t mode) {
    if (!s_driver_initialized) {
        return ESP8266_GPIO_ERR_INVALID_PARAM;
    }

    if (pin > 16) {
        return ESP8266_GPIO_ERR_INVALID_PARAM;
    }

    /* 
     * Команда AT+PINMODE=<pin>,<mode>
     * Режими: 0 - INPUT, 1 - OUTPUT, 2 - INPUT_PULLUP, 3 - OUTPUT_OPEN_DRAIN
     */
    return send_at_cmd_formatted("AT+PINMODE=%u,%u\r\n", pin, (unsigned int)mode);
}

esp8266_gpio_err_t esp8266_gpio_write(uint8_t pin, esp8266_gpio_level_t level) {
    if (!s_driver_initialized) {
        return ESP8266_GPIO_ERR_INVALID_PARAM;
    }

    if (pin > 16 || (level != ESP8266_GPIO_LEVEL_LOW && level != ESP8266_GPIO_LEVEL_HIGH)) {
        return ESP8266_GPIO_ERR_INVALID_PARAM;
    }

    /* Команда AT+PINWRITE=<pin>,<level> */
    return send_at_cmd_formatted("AT+PINWRITE=%u,%u\r\n", pin, (unsigned int)level);
}

esp8266_gpio_err_t esp8266_gpio_read(uint8_t pin, esp8266_gpio_level_t *out_level) {
    if (!s_driver_initialized || !out_level) {
        return ESP8266_GPIO_ERR_INVALID_PARAM;
    }

    if (pin > 16) {
        return ESP8266_GPIO_ERR_INVALID_PARAM;
    }

    uart_ring_buffer_clear(s_config.rx_buffer);

    /* Форматування та надсилання AT+PINREAD=<pin> */
    char cmd_buf[32];
    snprintf(cmd_buf, sizeof(cmd_buf), "AT+PINREAD=%u\r\n", pin);
    uart_tx_string(cmd_buf);

    uint32_t start_time = s_config.get_ticks_ms();
    bool parsed_value = false;
    esp8266_gpio_level_t read_val = ESP8266_GPIO_LEVEL_LOW;

    /*
     * Неблокуючий розбір відповіді виду "+PINREAD:<pin>,<val>" або "+PINREAD:<val>"
     * із подальшим підтвердженням "OK\r\n".
     */
    while ((s_config.get_ticks_ms() - start_time) < s_config.default_timeout_ms) {
        int read_idx = uart_ring_buffer_find(s_config.rx_buffer, "+PINREAD:");
        if (read_idx >= 0 && !parsed_value) {
            uint16_t avail = uart_ring_buffer_available(s_config.rx_buffer);
            /* Перевіряємо наявність символу нового рядка після маркера */
            for (uint16_t i = (uint16_t)read_idx; i < avail; i++) {
                uint16_t idx = (s_config.rx_buffer->tail + i) & (UART_RING_BUFFER_SIZE - 1);
                char c = (char)s_config.rx_buffer->buffer[idx];
                if (c == '0' || c == '1') {
                    read_val = (c == '1') ? ESP8266_GPIO_LEVEL_HIGH : ESP8266_GPIO_LEVEL_LOW;
                    parsed_value = true;
                }
            }
        }

        int ok_idx = uart_ring_buffer_find(s_config.rx_buffer, "OK\r\n");
        if (ok_idx >= 0) {
            uart_ring_buffer_skip(s_config.rx_buffer, (uint16_t)(ok_idx + 4));
            if (parsed_value) {
                *out_level = read_val;
                return ESP8266_GPIO_OK;
            }
            return ESP8266_GPIO_ERR_AT_ERROR;
        }

        int err_idx = uart_ring_buffer_find(s_config.rx_buffer, "ERROR\r\n");
        if (err_idx >= 0) {
            uart_ring_buffer_skip(s_config.rx_buffer, (uint16_t)(err_idx + 7));
            return ESP8266_GPIO_ERR_AT_ERROR;
        }

        if (s_config.delay_ms) {
            s_config.delay_ms(1);
        }
    }

    return ESP8266_GPIO_ERR_TIMEOUT;
}

esp8266_gpio_err_t esp8266_relay_init_safe(esp8266_relay_handle_t *relay, uint8_t pin, esp8266_gpio_level_t active_level) {
    if (!relay || !s_driver_initialized) {
        return ESP8266_GPIO_ERR_INVALID_PARAM;
    }

    relay->gpio_pin = pin;
    relay->active_level = active_level;
    relay->is_initialized = false;

    /*
     * Пасивний (безпечний) рівень — це стан, при якому реле знеструмлене.
     * Якщо реле вмикається високим рівнем (Active HIGH), пасивний рівень = LOW.
     * Якщо Active LOW, то пасивний рівень = HIGH.
     */
    esp8266_gpio_level_t safe_level = (active_level == ESP8266_GPIO_LEVEL_HIGH) ?
                                       ESP8266_GPIO_LEVEL_LOW : ESP8266_GPIO_LEVEL_HIGH;

    relay->current_level = safe_level;

    /*
     * АЛГОРИТМ БЕЗПЕКИ:
     * 1. Спочатку встановлюємо безпечний вихідний рівень через AT+PINWRITE,
     *    щоб при подальшому переведенні виводу у режим OUTPUT не виникло коротке
     *    імпульсне спрацьовування котушки реле (glitch / false toggle).
     */
    esp8266_gpio_write(pin, safe_level);

    /* 2. Налаштовуємо вивід як цифровий вихід (AT+PINMODE=pin,1) */
    esp8266_gpio_err_t err = esp8266_gpio_set_mode(pin, ESP8266_GPIO_MODE_OUTPUT);
    if (err != ESP8266_GPIO_OK) {
        return err;
    }

    /* 3. Повторно фіксуємо безпечний рівень для 100% надійності */
    err = esp8266_gpio_write(pin, safe_level);
    if (err != ESP8266_GPIO_OK) {
        return err;
    }

    relay->is_initialized = true;
    return ESP8266_GPIO_OK;
}

esp8266_gpio_err_t esp8266_relay_set_state(esp8266_relay_handle_t *relay, bool enable) {
    if (!relay || !relay->is_initialized) {
        return ESP8266_GPIO_ERR_INVALID_PARAM;
    }

    esp8266_gpio_level_t target_level = enable ? relay->active_level :
        ((relay->active_level == ESP8266_GPIO_LEVEL_HIGH) ? ESP8266_GPIO_LEVEL_LOW : ESP8266_GPIO_LEVEL_HIGH);

    esp8266_gpio_err_t err = esp8266_gpio_write(relay->gpio_pin, target_level);
    if (err == ESP8266_GPIO_OK) {
        relay->current_level = target_level;
    }
    return err;
}

esp8266_gpio_err_t esp8266_relay_toggle(esp8266_relay_handle_t *relay) {
    if (!relay || !relay->is_initialized) {
        return ESP8266_GPIO_ERR_INVALID_PARAM;
    }
    bool current_state = (relay->current_level == relay->active_level);
    return esp8266_relay_set_state(relay, !current_state);
}

const char* esp8266_gpio_err_to_string(esp8266_gpio_err_t err) {
    switch (err) {
        case ESP8266_GPIO_OK:
            return "Успішно (OK)";
        case ESP8266_GPIO_ERR_INVALID_PARAM:
            return "Некоректний параметр або дескриптор";
        case ESP8266_GPIO_ERR_TIMEOUT:
            return "Тайм-аут очікування відповіді UART";
        case ESP8266_GPIO_ERR_AT_ERROR:
            return "Модуль ESP8266 повернув стан ERROR";
        case ESP8266_GPIO_ERR_UART:
            return "Помилка послідовного інтерфейсу UART";
        case ESP8266_GPIO_ERR_UNRESPONSIVE:
            return "Модуль ESP8266 не відповідає на AT-запити";
        default:
            return "Невідома помилка";
    }
}
