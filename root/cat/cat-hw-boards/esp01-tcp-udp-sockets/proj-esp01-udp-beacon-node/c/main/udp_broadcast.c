/**
 * @file udp_broadcast.c
 * @brief Реалізація неблокуючого UDP-інтерфейсу з підтримкою широкомовної розсилки.
 */

#include "udp_broadcast.h"
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <fcntl.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>

#include "esp_log.h"

static const char *TAG = "UDP_SOCKET";

int udp_socket_create(void)
{
    // 1. Створення датаграмного сокета IPv4/UDP
    int sock_fd = socket(AF_INET, SOCK_DGRAM, IPPROTO_IP);
    if (sock_fd < 0) {
        ESP_LOGE(TAG, "Не вдалося створити UDP-сокет: errno %d (%s)", errno, strerror(errno));
        return -1;
    }

    // 2. Увімкнення опції широкомовної розсилки SO_BROADCAST
    int broadcast_enable = 1;
    if (setsockopt(sock_fd, SOL_SOCKET, SO_BROADCAST, &broadcast_enable, sizeof(broadcast_enable)) < 0) {
        ESP_LOGE(TAG, "Помилка встановлення опції SO_BROADCAST: errno %d (%s)", errno, strerror(errno));
        close(sock_fd);
        return -1;
    }

    // 3. Встановлення неблокуючого режиму O_NONBLOCK через fcntl
    int flags = fcntl(sock_fd, F_GETFL, 0);
    if (flags < 0 || fcntl(sock_fd, F_SETFL, flags | O_NONBLOCK) < 0) {
        ESP_LOGE(TAG, "Помилка встановлення режиму O_NONBLOCK: errno %d (%s)", errno, strerror(errno));
        close(sock_fd);
        return -1;
    }

    // 4. Прив'язка сокета до локальної адреси та порту
    struct sockaddr_in bind_addr;
    memset(&bind_addr, 0, sizeof(bind_addr));
    bind_addr.sin_family = AF_INET;
    bind_addr.sin_port = htons(UDP_PORT);
    bind_addr.sin_addr.s_addr = htonl(INADDR_ANY);

    if (bind(sock_fd, (struct sockaddr *)&bind_addr, sizeof(bind_addr)) < 0) {
        ESP_LOGE(TAG, "Помилка зв'язування сокета (bind): errno %d (%s)", errno, strerror(errno));
        close(sock_fd);
        return -1;
    }

    ESP_LOGI(TAG, "Неблокуючий UDP-сокет успішно створено (fd=%d, порт=%d).", sock_fd, UDP_PORT);
    return sock_fd;
}

bool udp_socket_send_broadcast(int sock_fd, const telemetry_pkt_t *pkt)
{
    if (sock_fd < 0 || pkt == NULL) {
        return false;
    }

    struct sockaddr_in dest_addr;
    memset(&dest_addr, 0, sizeof(dest_addr));
    dest_addr.sin_family = AF_INET;
    dest_addr.sin_port = htons(UDP_PORT);
    inet_pton(AF_INET, BROADCAST_IP_ADDR, &dest_addr.sin_addr.s_addr);

    ssize_t sent_bytes = sendto(sock_fd, pkt, sizeof(telemetry_pkt_t), 0,
                                (struct sockaddr *)&dest_addr, sizeof(dest_addr));

    if (sent_bytes < 0) {
        if (errno == EWOULDBLOCK || errno == EAGAIN) {
            ESP_LOGW(TAG, "Буфер відправки переповнений (EWOULDBLOCK). Датаграму пропущено.");
        } else {
            ESP_LOGE(TAG, "Помилка відправки sendto: errno %d (%s)", errno, strerror(errno));
        }
        return false;
    }

    ESP_LOGI(TAG, "Надіслано широкомовний пакет (seq=%u, розмір=%d байт).",
             (unsigned int)pkt->sequence, (int)sent_bytes);
    return true;
}

int udp_socket_receive(int sock_fd, uint8_t *buffer, size_t max_len)
{
    if (sock_fd < 0 || buffer == NULL || max_len == 0) {
        return -1;
    }

    struct sockaddr_in source_addr;
    socklen_t addr_len = sizeof(source_addr);

    ssize_t rx_bytes = recvfrom(sock_fd, buffer, max_len - 1, 0,
                                (struct sockaddr *)&source_addr, &addr_len);

    if (rx_bytes < 0) {
        if (errno == EWOULDBLOCK || errno == EAGAIN) {
            return 0;
        }
        ESP_LOGE(TAG, "Помилка читання recvfrom: errno %d (%s)", errno, strerror(errno));
        return -1;
    }

    buffer[rx_bytes] = '\0';
    char sender_ip[INET_ADDRSTRLEN];
    inet_ntop(AF_INET, &source_addr.sin_addr, sender_ip, sizeof(sender_ip));

    ESP_LOGI(TAG, "Отримано %d байт від %s:%d",
             (int)rx_bytes, sender_ip, ntohs(source_addr.sin_port));

    return (int)rx_bytes;
}

void udp_socket_close(int *sock_fd)
{
    if (sock_fd && *sock_fd >= 0) {
        close(*sock_fd);
        ESP_LOGI(TAG, "Сокет fd=%d закрито, ресурси вивільнено.", *sock_fd);
        *sock_fd = -1;
    }
}
