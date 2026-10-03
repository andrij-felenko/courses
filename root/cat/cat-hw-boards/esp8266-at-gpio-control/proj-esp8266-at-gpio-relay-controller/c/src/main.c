#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>
#include "uart_driver.h"
#include "esp8266_at_gpio.h"

/**
 * @file main.c
 * @brief Приклад практичного застосування C-драйвера ESP8266 AT GPIO на хост-мікроконтролері.
 * 
 * Демонструє ініціалізацію UART, симуляцію відповіді модуля ESP8266 в реальному часі,
 * безпечне налаштування виводів силового реле, опитування цифрових датчиків/кнопок
 * та коректну обробку втрати зв'язку або помилок парсингу AT-команд.
 */

static uart_ring_buffer_t g_uart_rx_ring;
static uint32_t g_simulated_ticks_ms = 0;

/* Симуляція системного лічильника часу (мілісекунди) */
static uint32_t get_system_ticks_ms(void) {
    return g_simulated_ticks_ms;
}

/* Симуляція блокуючої затримки з просуванням системного часу */
static void delay_ms(uint32_t ms) {
    g_simulated_ticks_ms += ms;
}

/* Перехоплення переданих хостом AT-команд та симуляція вхідних відповідей від ESP8266 */
void uart_tx_string(const char *str) {
    printf("[UART TX -> ESP8266]: %s", str);

    /* Апаратний емулятор відповідей інтерпретатора ESP8266 AT */
    if (strstr(str, "AT\r\n") != NULL || strstr(str, "ATE0\r\n") != NULL) {
        const char *resp = "OK\r\n";
        for (size_t i = 0; i < strlen(resp); i++) {
            uart_ring_buffer_push(&g_uart_rx_ring, (uint8_t)resp[i]);
        }
    } else if (strstr(str, "AT+PINMODE=") != NULL) {
        const char *resp = "OK\r\n";
        for (size_t i = 0; i < strlen(resp); i++) {
            uart_ring_buffer_push(&g_uart_rx_ring, (uint8_t)resp[i]);
        }
    } else if (strstr(str, "AT+PINWRITE=") != NULL) {
        /* Симуляція відмови для неіснуючого пина 99 */
        if (strstr(str, "99") != NULL) {
            const char *resp = "ERROR\r\n";
            for (size_t i = 0; i < strlen(resp); i++) {
                uart_ring_buffer_push(&g_uart_rx_ring, (uint8_t)resp[i]);
            }
        } else {
            const char *resp = "OK\r\n";
            for (size_t i = 0; i < strlen(resp); i++) {
                uart_ring_buffer_push(&g_uart_rx_ring, (uint8_t)resp[i]);
            }
        }
    } else if (strstr(str, "AT+PINREAD=4") != NULL) {
        /* Симуляція зчитування стану кнопки на GPIO4 (повертаємо High = 1) */
        const char *resp = "+PINREAD:4,1\r\nOK\r\n";
        for (size_t i = 0; i < strlen(resp); i++) {
            uart_ring_buffer_push(&g_uart_rx_ring, (uint8_t)resp[i]);
        }
    } else if (strstr(str, "AT+PINREAD=12") != NULL) {
        /* Симуляція тайм-ауту/втрати зв'язку при зчитуванні GPIO12 (нічого не відправляємо у буфер) */
        printf("  [СИМУЛЯЦІЯ]: Модуль ESP8266 не відповідає на вивід GPIO12 (імітація обриву лінії UART)...\n");
    }
}

bool uart_init(uint32_t baudrate) {
    (void)baudrate;
    uart_ring_buffer_init(&g_uart_rx_ring);
    g_simulated_ticks_ms = 100;
    return true;
}

int main(void) {
    printf("===============================================================\n");
    printf("  ДРАЙВЕР ESP8266 AT GPIO ДЛЯ ХОСТ-МІКРОКОНТРОЛЕРА (C99)\n");
    printf("===============================================================\n\n");

    /* КРОК 1: Ініціалізація апаратного UART хост-контролера */
    printf("[ІНІЦІАЛІЗАЦІЯ] Запуск апаратного послідовного порту UART (115200 baud)...\n");
    if (!uart_init(115200)) {
        printf("[ПОМИЛКА] Не вдалося ініціалізувати послідовний порт!\n");
        return EXIT_FAILURE;
    }

    /* КРОК 2: Заповнення структури конфігурації C-драйвера ESP8266 */
    esp8266_gpio_config_t config = {
        .default_timeout_ms = 1000,
        .boot_stabilization_delay_ms = 500,
        .disable_echo = true,
        .rx_buffer = &g_uart_rx_ring,
        .get_ticks_ms = get_system_ticks_ms,
        .delay_ms = delay_ms
    };

    /* КРОК 3: Старт драйвера з урахуванням апаратних затримок strapping pins */
    printf("[ІНІЦІАЛІЗАЦІЯ] Старт драйвера ESP8266 GPIO (затримка стабілізації 500 мс)...\n");
    esp8266_gpio_err_t err = esp8266_gpio_init(&config);
    if (err != ESP8266_GPIO_OK) {
        printf("[ПОМИЛКА] Ініціалізація ESP8266 завершилася зі збоєм: %s\n", esp8266_gpio_err_to_string(err));
        return EXIT_FAILURE;
    }
    printf("[УСПІХ] Модуль ESP8266 успішно підтвердив зв'язок (OK).\n\n");

    /* КРОК 4: Безопасне налаштування виводу силового реле на GPIO5 */
    printf("[РЕЛЕ] Безпечна конфігурація силового реле на GPIO5 (Active HIGH)...\n");
    esp8266_relay_handle_t relay_fan;
    err = esp8266_relay_init_safe(&relay_fan, 5, ESP8266_GPIO_LEVEL_HIGH);
    if (err != ESP8266_GPIO_OK) {
        printf("[ПОМИЛКА] Помилка налаштування реле: %s\n", esp8266_gpio_err_to_string(err));
    } else {
        printf("[УСПІХ] Реле ініціалізовано в безпечному вимкненому стані.\n");
    }
    printf("\n");

    /* КРОК 5: Перемикання станів реле з перевіркою підтверджень OK */
    printf("[РЕЛЕ] Увімкнення вентилятора (relay set state -> true)...\n");
    err = esp8266_relay_set_state(&relay_fan, true);
    printf("  Статус виконання: %s\n\n", esp8266_gpio_err_to_string(err));

    printf("[РЕЛЕ] Перемикання стану реле (toggle)...\n");
    err = esp8266_relay_toggle(&relay_fan);
    printf("  Статус виконання: %s\n\n", esp8266_gpio_err_to_string(err));

    /* КРОК 6: Налаштування та зчитування цифрового виводу (кнопки) на GPIO4 */
    printf("[GPIO INPUT] Конфігурування GPIO4 у режим INPUT_PULLUP...\n");
    err = esp8266_gpio_set_mode(4, ESP8266_GPIO_MODE_INPUT_PULLUP);
    printf("  Статус PINMODE: %s\n", esp8266_gpio_err_to_string(err));

    esp8266_gpio_level_t button_level;
    printf("[GPIO INPUT] Зчитування стану GPIO4 (AT+PINREAD=4)...\n");
    err = esp8266_gpio_read(4, &button_level);
    if (err == ESP8266_GPIO_OK) {
        printf("[УСПІХ] Зчитаний рівень GPIO4: %s (%d)\n",
               (button_level == ESP8266_GPIO_LEVEL_HIGH) ? "HIGH" : "LOW", button_level);
    } else {
        printf("[ПОМИЛКА] Не вдалося зчитати GPIO4: %s\n", esp8266_gpio_err_to_string(err));
    }
    printf("\n");

    /* КРОК 7: Демонстрація перевірки strapping pins (GPIO0, GPIO2, GPIO15) */
    printf("[STRAPPING PINS] Перевірка завантажувальних виводів:\n");
    uint8_t test_pins[] = {0, 2, 4, 5, 15};
    for (size_t i = 0; i < sizeof(test_pins)/sizeof(test_pins[0]); i++) {
        uint8_t pin = test_pins[i];
        bool is_strap = esp8266_gpio_is_strapping_pin(pin);
        printf("  GPIO%-2d: %s\n", pin, is_strap ? "УВАГА! Strapping Pin (захищено)" : "Звичайний GPIO");
    }
    printf("\n");

    /* КРОК 8: Демонстрація обробки помилки AT (спроба запису на неіснуючий пин 99) */
    printf("[ОБРОБКА ПОМИЛОК] Перевірка реакції на відповідь ERROR (AT+PINWRITE=99,1)...\n");
    err = esp8266_gpio_write(99, ESP8266_GPIO_LEVEL_HIGH);
    printf("  Отриманий результат: %s (код: %d)\n\n", esp8266_gpio_err_to_string(err), err);

    /* КРОК 9: Демонстрація обробки тайм-ауту втрати зв'язку (GPIO12) */
    printf("[ОБРОБКА ПОМИЛОК] Перевірка реакції на втрату зв'язку / тайм-аут UART (GPIO12)...\n");
    err = esp8266_gpio_read(12, &button_level);
    printf("  Отриманий результат: %s (код: %d)\n\n", esp8266_gpio_err_to_string(err), err);

    printf("===============================================================\n");
    printf("  ДЕМОНСТРАЦІЮ ДРАЙВЕРА УСПІШНО ЗАВЕРШЕНО\n");
    printf("===============================================================\n");

    return EXIT_SUCCESS;
}
