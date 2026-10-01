/*
 * user_main.c — Приклад прошивки мовою C для модулів ESP-01 та ESP-01S (ESP8266 RTOS SDK / ESP-IDF)
 *
 * Призначення:
 * Ініціалізація периферійних модулів UART та GPIO, виведення діагностичної
 * інформації про розпіновку й режими завантаження ESP-01/ESP-01S, а також
 * періодичне блимання вбудованим індикаторним світлодіодом.
 *
 * Особливості ESP-01 vs ESP-01S:
 * 1. ESP-01:
 *    - Індикаторний світлодіод синього кольору зазвичай підключений до TXD (GPIO1).
 *    - Не має вбудованих резисторів підтяжки на GPIO0, GPIO2, CH_PD, RST (потрібні зовнішні 10 кОм до 3.3V).
 * 2. ESP-01S:
 *    - Індикаторний світлодіод підключений до GPIO2 (активний низький рівень: LOW = увімкнено).
 *    - Має вбудовані підтягувальні резистори 12 кОм на GPIO0, GPIO2, CH_PD, RST.
 */

#include <stdio.h>
#include <stdbool.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"
#include "driver/uart.h"
#include "esp_log.h"

// Визначення пінів світлодіода для ревізій модулів
// ESP-01S містить світлодіод на GPIO2 (Active LOW)
// ESP-01 містить світлодіод на GPIO1 / TXD (Active LOW)
#define LED_GPIO_ESP01S   GPIO_NUM_2
#define LED_GPIO_ESP01    GPIO_NUM_1

// Використовувана швидкість передачі даних послідовного порту
#define UART_BAUD_RATE    115200
#define UART_PORT_NUM     UART_NUM_0
#define UART_BUF_SIZE     256

// Тег для виводу логів ESP-IDF
static const char *TAG = "ESP01_DIAG";

/**
 * @brief Ініціалізація апаратного модуля UART0 для діагностичного виводу
 */
static void init_uart(void)
{
    uart_config_t uart_config = {
        .baud_rate = UART_BAUD_RATE,
        .data_bits = UART_DATA_8_BITS,
        .parity    = UART_PARITY_DISABLE,
        .stop_bits = UART_STOP_BITS_1,
        .flow_ctrl = UART_HW_FLOWCTRL_DISABLE,
    };

    // Налаштування параметрів UART0
    ESP_ERROR_CHECK(uart_param_config(UART_PORT_NUM, &uart_config));
    
    // Встановлення стандартних пінів UART0 (TX = GPIO1, RX = GPIO3)
    ESP_ERROR_CHECK(uart_set_pin(UART_PORT_NUM, UART_PIN_NO_CHANGE, UART_PIN_NO_CHANGE,
                                  UART_PIN_NO_CHANGE, UART_PIN_NO_CHANGE));
    
    // Встановлення драйвера UART без кільцевого буфера прийому для спрощеного виводу
    ESP_ERROR_CHECK(uart_driver_install(UART_PORT_NUM, UART_BUF_SIZE, 0, 0, NULL, 0));
}

/**
 * @brief Ініціалізація виводів GPIO для керування світлодіодами ESP-01 та ESP-01S
 */
static void init_gpio(void)
{
    // Конфігурація GPIO2 (для ESP-01S)
    gpio_config_t io_conf_esp01s = {
        .pin_bit_mask = (1ULL << LED_GPIO_ESP01S),
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };
    gpio_config(&io_conf_esp01s);

    // Початковий стан: вимкнено (HIGH, оскільки світлодіод підключений за схемою Active LOW)
    gpio_set_level(LED_GPIO_ESP01S, 1);
}

/**
 * @brief Виведення довідкової інформації про розпіновку та підключення модуля
 */
static void print_esp01_info(void)
{
    printf("\r\n=======================================================\r\n");
    printf("   Огляд та діагностика модулів ESP-01 / ESP-01S (C SDK) \r\n");
    printf("=======================================================\r\n");
    printf("Параметри живлення:\r\n");
    printf(" - VCC: 3.3 В (максимальний струм до 300 мА у піках TX)\r\n");
    printf(" - GND: Загальний мінус\r\n");
    printf("\r\nРежими завантаження (Boot Pin States):\r\n");
    printf(" - GPIO0 = LOW  (0V)  -> Режим прошивки (UART Download)\r\n");
    printf(" - GPIO0 = HIGH (3.3V)-> Нормальний режим виконання програми\r\n");
    printf(" - GPIO2 = HIGH (3.3V)-> Обов'язкова підтяжка для успішного старту\r\n");
    printf(" - CH_PD / EN = HIGH  -> Увімкнення кристала ESP8266\r\n");
    printf(" - RST = HIGH         -> Скидання активне при LOW\r\n");
    printf("\r\nВідмінності ревізій:\r\n");
    printf(" - ESP-01 : Потрібні зовнішні підтягувальні резистори 10 кОм\r\n");
    printf(" - ESP-01S: Вбудовані резистори 12 кОм на GPIO0, GPIO2, CH_PD, RST\r\n");
    printf("=======================================================\r\n\r\n");
}

/**
 * @brief Головне завдання FreeRTOS для блимання світлодіодом та виведення статусу
 */
static void blink_task(void *arg)
{
    (void)arg;
    uint32_t loop_counter = 0;
    bool led_state = false;

    print_esp01_info();

    while (1) {
        loop_counter++;
        led_state = !led_state;

        // Інвертована логіка (Active LOW):
        // led_state == true  -> gpio_level = 0 (увімкнено)
        // led_state == false -> gpio_level = 1 (вимкнено)
        uint32_t level = led_state ? 0 : 1;
        gpio_set_level(LED_GPIO_ESP01S, level);

        ESP_LOGI(TAG, "[Цикл #%lu] Світлодіод GPIO2: %s (Логічний рівень pin: %lu)",
                 (unsigned long)loop_counter,
                 led_state ? "УВІМКНЕНО (LOW)" : "ВИМКНЕНО (HIGH)",
                 (unsigned long)level);

        // Затримка 1000 мс (1 секунда)
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}

/**
 * @brief Головна точка входу прошивки C (ESP-IDF / ESP8266 RTOS SDK)
 */
void app_main(void)
{
    // Ініціалізація периферії
    init_uart();
    init_gpio();

    ESP_LOGI(TAG, "Ініціалізацію завершено. Запуск тестового циклу...");

    // Створення фонового завдання FreeRTOS
    xTaskCreate(blink_task, "blink_task", 2048, NULL, 5, NULL);
}
