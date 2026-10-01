#include "esp01_socket.h"
#include <stdio.h>

static esp01_socket_t g_esp01_sock;

// Заглушка апаратної передачі байтів через UART
void uart_send_bytes(const uint8_t *data, uint16_t len) {
    (void)data;
    (void)len;
}

// Callback-функція обробки вхідних кадрів +IPD
void esp01_on_data_received(uint8_t link_id, const uint8_t *data, uint16_t len) {
    printf("[ESP-01] Отримано %d байт з сокета %d\n", len, link_id);
    (void)data;
}

int main(void) {
    uint32_t system_time_ms = 0;

    // Ініціалізація сокетного модуля ESP-01
    esp01_socket_init(&g_esp01_sock);

    const uint8_t payload[] = "GET /api/v1/status HTTP/1.1\r\nHost: example.com\r\n\r\n";
    bool send_requested = false;

    // Головний неблокувальний цикл мікроконтролера
    while (1) {
        system_time_ms++;

        // Спроба асинхронної відправки даних
        if (system_time_ms == 100 && !send_requested) {
            if (esp01_send_async(&g_esp01_sock, 0, payload, sizeof(payload) - 1)) {
                send_requested = true;
            }
        }

        // Опитування та просування станів кінцевого автомата
        esp01_socket_poll(&g_esp01_sock, system_time_ms);
    }

    return 0;
}
