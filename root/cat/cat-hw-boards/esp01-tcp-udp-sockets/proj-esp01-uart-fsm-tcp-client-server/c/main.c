#include <stdio.h>
#include <string.h>
#include "at_parser.h"

// Приклад колбека успішного виконання AT-команди
static void on_at_ok(void *user_ctx) {
    (void)user_ctx;
    printf("[AT EVENT] Отримано статус підтвердження: OK\n");
}

// Приклад колбека помилки виконання AT-команди
static void on_at_error(void *user_ctx) {
    (void)user_ctx;
    printf("[AT EVENT] Отримано сповіщення про помилку: ERROR\n");
}

// Приклад колбека прийому мережевих даних TCP/UDP сокета (+IPD)
static void on_at_ipd_data(uint8_t link_id, const uint8_t *data, uint16_t len, void *user_ctx) {
    (void)user_ctx;
    printf("[AT EVENT] Отримано пакунок сокета ID=%d, довжина=%u байт: \"", link_id, len);
    for (uint16_t i = 0; i < len; i++) {
        putchar((char)data[i]);
    }
    printf("\"\n");
}

int main(void) {
    at_parser_t parser;
    
    // Ініціалізація парсера та реєстрація обробників подій
    at_parser_init(&parser, NULL);
    at_parser_set_callbacks(&parser, on_at_ok, on_at_error, on_at_ipd_data);
    
    // Симуляція асинхронного потоку даних з UART від ESP-01
    const char *simulated_uart_stream = 
        "\r\nOK\r\n"
        "+IPD,0,12:Hello Socket\r\n"
        "\r\nERROR\r\n";
    
    printf("--- Запуск неблокувального посимвольного розбору буфера UART ---\n");
    
    // Симуляція надходження байтів по одному з UART-кільцевого буфера
    size_t stream_len = strlen(simulated_uart_stream);
    for (size_t i = 0; i < stream_len; i++) {
        at_parser_process_char(&parser, simulated_uart_stream[i]);
    }
    
    printf("--- Симуляцію розбору успішно завершено ---\n");
    return 0;
}
