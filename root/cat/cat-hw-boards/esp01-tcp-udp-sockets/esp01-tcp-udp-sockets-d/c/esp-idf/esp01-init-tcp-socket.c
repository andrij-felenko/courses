#include <stdio.h>
#include <string.h>
#include <stdbool.h>

// Функція ініціалізації TCP-сокета через UART
bool esp01_init_tcp_socket(uint8_t link_id, const char* remote_ip, uint16_t port) {
    char cmd_buf[128];

    // Налаштування мультиплексованого режиму CIPMUX=1
    snprintf(cmd_buf, sizeof(cmd_buf), "AT+CIPMUX=1\r\n");
    // Передача cmd_buf у послідовний порт UART...
    // Очікування відповіді "OK" від модуля

    // Формування команди відкриття TCP сокета
    snprintf(cmd_buf, sizeof(cmd_buf), "AT+CIPSTART=%u,\"TCP\",\"%s\",%u,7200\r\n", 
             link_id, remote_ip, port);

    // Відправка команди в UART та аналіз результату
    // Очікування парсером відповідей "CONNECT", "OK" або "ERROR"
    return true;
}
