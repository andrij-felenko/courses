#include <stdint.h>
#include <stdbool.h>
#include <string.h>

typedef enum {
    SOCKET_OK = 0,
    SOCKET_ERR_CONNECT,
    SOCKET_ERR_SEND,
    SOCKET_ERR_TIMEOUT,
    SOCKET_ERR_CLOSED
} socket_status_t;

// Безпечне встановлення TCP-з'єднання та надсилання даних
socket_status_t esp01_send_tcp_data(uint8_t link_id, const char *host, uint16_t port, const uint8_t *data, uint16_t len) {
    // 1. Формування та надсилання команди ініціалізації сокета
    // AT+CIPSTART=<link_id>,"TCP","<host>",<port>
    if (!uart_send_cmd_expect("AT+CIPSTART=%d,\"TCP\",\"%s\",%d\r\n", "CONNECT", 5000)) {
        // При помилці зв'язку гарантовано закриваємо сокет для вивільнення DRAM
        uart_send_cmd("AT+CIPCLOSE=%d\r\n", link_id);
        return SOCKET_ERR_CONNECT;
    }

    // 2. Ініціалізація двофазного режиму відправки
    if (!uart_send_cmd_expect("AT+CIPSEND=%d,%d\r\n", ">", 2000)) {
        uart_send_cmd("AT+CIPCLOSE=%d\r\n", link_id);
        return SOCKET_ERR_SEND;
    }

    // 3. Передача двійкового навантаження та очікування підтвердження
    uart_write_bytes(data, len);
    if (!uart_wait_response("SEND OK", 3000)) {
        uart_send_cmd("AT+CIPCLOSE=%d\r\n", link_id);
        return SOCKET_ERR_SEND;
    }

    // 4. Коректне закриття сокета після завершення сесії
    uart_send_cmd_expect("AT+CIPCLOSE=%d\r\n", "OK", 1000);
    return SOCKET_OK;
}
