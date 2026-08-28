#include <string.h>
#include "lwip/sockets.h"
#include "esp_log.h"

static const char *TAG = "tcp";

void tcp_client(void)
{
    // 1) створити TCP-сокет: SOCK_STREAM — надійний потік байтів (TCP)
    int sock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (sock < 0) { ESP_LOGE(TAG, "socket: errno %d", errno); return; }

    // 2) описати, куди під'єднатися: адреса й порт сервера
    struct sockaddr_in server = {
        .sin_family = AF_INET,
        .sin_port   = htons(4000),
    };
    inet_pton(AF_INET, "192.168.1.20", &server.sin_addr);  // текст IP → число

    // 3) встановити з'єднання (тут проходить рукостискання TCP)
    if (connect(sock, (struct sockaddr *)&server, sizeof(server)) < 0) {
        ESP_LOGE(TAG, "connect: errno %d", errno);
        close(sock);
        return;
    }

    // 4) надіслати запит — адресу повторювати не треба, вона в з'єднанні
    const char *req = "STATUS?\n";
    send(sock, req, strlen(req), 0);

    // 5) прочитати відповідь; recv віддає рівно стільки, скільки вже прийшло
    char buf[256];
    int n = recv(sock, buf, sizeof(buf) - 1, 0);
    if (n > 0) {
        buf[n] = '\0';
        ESP_LOGI(TAG, "відповідь сервера: %s", buf);
    }

    close(sock);   // коректно закрити з'єднання
}
