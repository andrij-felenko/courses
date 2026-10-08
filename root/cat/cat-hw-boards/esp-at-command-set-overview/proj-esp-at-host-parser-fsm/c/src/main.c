#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#include "ring_buffer.h"
#include "esp_at_parser.h"

/**
 * @file main.c
 * @brief Приклад інтеграції FSM-парсера ESP-AT в основний цикл хост-мікроконтролера.
 */

#define RX_BUFFER_SIZE 256

/* Глобальні системні змінні для симуляції */
static uint8_t rx_raw_buffer[RX_BUFFER_SIZE];
static ring_buffer_t uart_rx_ring_buf;
static esp_at_parser_t at_parser;
static uint32_t mock_system_ticks_ms = 1000;

/**
 * @brief Симуляція повернення системних тиків таймера (мс).
 */
static uint32_t get_sys_tick_ms(void) {
    return mock_system_ticks_ms;
}

/**
 * @brief Симуляція надходження даних від модуля ESP8266 через переривання UART ISR.
 */
static void uart_isr_simulate_rx_bytes(const char *data) {
    size_t len = strlen(data);
    for (size_t i = 0; i < len; i++) {
        ring_buffer_push(&uart_rx_ring_buf, (uint8_t)data[i]);
    }
}

/**
 * @brief Симуляція передачі AT-команди в UART хостом.
 */
static void uart_send_string(const char *cmd) {
    printf("[UART TX] -> %s", cmd);
}

/* --- Реалізація колбеків статусів AT-відповідей --- */

static void cb_on_at_ok(esp_at_status_t status, void *user_data) {
    (void)status;
    (void)user_data;
    printf("[EVENT] Status OK received! Command executed successfully.\n");
}

static void cb_on_at_error(esp_at_status_t status, void *user_data) {
    (void)status;
    (void)user_data;
    printf("[EVENT] Status ERROR received! Command failed.\n");
}

static void cb_on_at_busy(esp_at_status_t status, void *user_data) {
    (void)status;
    (void)user_data;
    printf("[EVENT] Status BUSY received! Module processing previous request.\n");
}

static void cb_on_at_timeout(esp_at_status_t status, void *user_data) {
    (void)status;
    (void)user_data;
    printf("[EVENT] Timeout triggered! No response from ESP8266 within specified window.\n");
}

static void cb_on_at_line(const char *line, size_t length, void *user_data) {
    (void)length;
    (void)user_data;
    printf("[UART RX Line] <- \"%s\"\n", line);
}

int main(void) {
    printf("=========================================================\n");
    printf("   ESP-AT FSM Parser Demo: Non-blocking Character Parsing\n");
    printf("=========================================================\n\n");

    /* 1. Ініціалізація кільцевого буфера */
    ring_buffer_init(&uart_rx_ring_buf, rx_raw_buffer, RX_BUFFER_SIZE);

    /* 2. Ініціалізація FSM-парсера AT-відповідей */
    esp_at_parser_init(&at_parser, &uart_rx_ring_buf, get_sys_tick_ms);

    /* 3. Реєстрація функцій зворотного виклику */
    esp_at_parser_register_callbacks(&at_parser,
                                       cb_on_at_ok,
                                       cb_on_at_error,
                                       cb_on_at_busy,
                                       cb_on_at_timeout);
    esp_at_parser_register_line_callback(&at_parser, cb_on_at_line);

    /* --- Сценарій 1: Успішне виконання команди AT --- */
    printf("--- Test Scenario 1: Command AT (Expect OK) ---\n");
    uart_send_string("AT\r\n");
    esp_at_parser_start_command(&at_parser, 1000); /* Таймаут 1000 мс */

    /* Імітуємо надходження відповіді "AT\r\n\r\nOK\r\n" у буфер перериванням */
    uart_isr_simulate_rx_bytes("AT\r\n\r\nOK\r\n");

    /* Основний цикл: неблокуюча обробка та перевірка таймауту */
    esp_at_parser_process_buffer(&at_parser);
    esp_at_parser_check_timeout(&at_parser);
    printf("Parser busy state: %s\n\n", esp_at_parser_is_busy(&at_parser) ? "YES" : "NO");

    /* --- Сценарій 2: Команда завершилася помилкою ERROR --- */
    printf("--- Test Scenario 2: Invalid Command (Expect ERROR) ---\n");
    mock_system_ticks_ms += 200;
    uart_send_string("AT+INVALID_CMD\r\n");
    esp_at_parser_start_command(&at_parser, 1000);

    /* Імітуємо надходження відповіді "ERROR\r\n" */
    uart_isr_simulate_rx_bytes("ERROR\r\n");

    esp_at_parser_process_buffer(&at_parser);
    esp_at_parser_check_timeout(&at_parser);
    printf("Parser busy state: %s\n\n", esp_at_parser_is_busy(&at_parser) ? "YES" : "NO");

    /* --- Сценарій 3: Виявлення таймауту очікування відповіді --- */
    printf("--- Test Scenario 3: Timeout Detection (No Response) ---\n");
    mock_system_ticks_ms += 500;
    uart_send_string("AT+CWJAP?\r\n");
    esp_at_parser_start_command(&at_parser, 1000); /* Очікуємо 1000 мс */

    /* У буфер нічого не надходить... Симулюємо сплив 1200 мс */
    mock_system_ticks_ms += 1200;

    esp_at_parser_process_buffer(&at_parser);
    esp_at_parser_check_timeout(&at_parser);
    printf("Parser busy state after timeout: %s\n\n", esp_at_parser_is_busy(&at_parser) ? "YES" : "NO");

    /* --- Сценарій 4: Отримання інформаційного кадру та статусу BUSY --- */
    printf("--- Test Scenario 4: Information Lines & Busy Status ---\n");
    mock_system_ticks_ms += 100;
    uart_send_string("AT+GMR\r\n");
    esp_at_parser_start_command(&at_parser, 2000);

    uart_isr_simulate_rx_bytes("AT version:1.7.4.0\r\nSDK version:3.0.4\r\nbusy p...\r\nOK\r\n");

    esp_at_parser_process_buffer(&at_parser);
    esp_at_parser_check_timeout(&at_parser);
    printf("Parser busy state: %s\n\n", esp_at_parser_is_busy(&at_parser) ? "YES" : "NO");

    printf("=========================================================\n");
    printf("   Demo Completed Successfully.\n");
    printf("=========================================================\n");

    return 0;
}
