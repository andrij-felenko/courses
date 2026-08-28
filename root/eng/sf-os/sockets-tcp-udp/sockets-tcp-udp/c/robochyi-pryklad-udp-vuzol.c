#include <string.h>
#include "lwip/sockets.h"      // BSD-сокети поверх lwIP
#include "esp_log.h"

static const char *TAG = "udp";

void udp_echo(void)
{
    // 1) створити UDP-сокет: AF_INET — IPv4, SOCK_DGRAM — датаграми (UDP)
    int sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (sock < 0) { ESP_LOGE(TAG, "socket: errno %d", errno); return; }

    // 2) закріпити сокет за портом 3333 на всіх інтерфейсах пристрою
    struct sockaddr_in me = {
        .sin_family      = AF_INET,
        .sin_port        = htons(3333),        // порт у мережевому порядку байтів
        .sin_addr.s_addr = htonl(INADDR_ANY),  // слухати на будь-якій адресі
    };
    if (bind(sock, (struct sockaddr *)&me, sizeof(me)) < 0) {
        ESP_LOGE(TAG, "bind: errno %d", errno);
        close(sock);
        return;
    }

    char buf[128];
    while (1) {
        // 3) чекати датаграму; recvfrom заразом віддає адресу відправника
        struct sockaddr_in from;
        socklen_t from_len = sizeof(from);
        int n = recvfrom(sock, buf, sizeof(buf) - 1, 0,
                         (struct sockaddr *)&from, &from_len);
        if (n < 0) { ESP_LOGE(TAG, "recvfrom: errno %d", errno); break; }

        buf[n] = '\0';
        ESP_LOGI(TAG, "прийнято %d байтів: %s", n, buf);

        // 4) відіслати ту саму порцію назад — туди, звідки прийшла
        sendto(sock, buf, n, 0, (struct sockaddr *)&from, from_len);
    }
    close(sock);
}
