#include "lwip/sockets.h"
#include "lwip/netdb.h"
#include <string.h>

void send_telemetry_lwip(const char* host, uint16_t port, const uint8_t* payload, size_t len) {
    struct sockaddr_in dest_addr;
    dest_addr.sin_addr.s_addr = inet_addr(host);
    dest_addr.sin_family = AF_INET;
    dest_addr.sin_port = htons(port);
    
    // Створення BSD сокета
    int sock = socket(AF_INET, SOCK_STREAM, IPPROTO_IP);
    if (sock < 0) {
        return;
    }
    
    // Підключення до сервера
    if (connect(sock, (struct sockaddr *)&dest_addr, sizeof(dest_addr)) != 0) {
        close(sock);
        return;
    }
    
    // Відправка буфера даних
    send(sock, payload, len, 0);
    
    // Прийом відповіді
    uint8_t rx_buffer[128];
    int len_rx = recv(sock, rx_buffer, sizeof(rx_buffer) - 1, 0);
    
    // Закриття сокета
    shutdown(sock, 0);
    close(sock);
}
