#include <string.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define DNS_PORT 53
#define DNS_BUFFER_SIZE 512

static const char *TAG_DNS = "dns_server";

void dns_server_task(void *pvParameters) {
    uint8_t buffer[DNS_BUFFER_SIZE];
    struct sockaddr_in server_addr, client_addr;
    socklen_t client_len = sizeof(client_addr);

    int sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (sock < 0) {
        ESP_LOGE(TAG_DNS, "Не вдалося створити UDP сокет");
        vTaskDelete(NULL);
        return;
    }

    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    server_addr.sin_port = htons(DNS_PORT);

    if (bind(sock, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        ESP_LOGE(TAG_DNS, "Помилка прив'язки UDP порту 53");
        close(sock);
        vTaskDelete(NULL);
        return;
    }

    ESP_LOGI(TAG_DNS, "DNS Catch-all сервер успішно запущено на порту 53");

    while (1) {
        int len = recvfrom(sock, buffer, sizeof(buffer), 0,
                           (struct sockaddr *)&client_addr, &client_len);
        if (len < 12) {
            continue; // Пакет пошкоджений або коротший за заголовок DNS
        }

        // Прапорці відповіді: QR=1 (відповідь), AA=1 (авторитетна), RA=1, RCODE=0 (успіх)
        buffer[2] = 0x81;
        buffer[3] = 0x80;

        // Встановлюємо кількість відповідей ANCOUNT = 1
        buffer[6] = 0x00;
        buffer[7] = 0x01;

        // Обнуляємо лічильники NSCOUNT та ARCOUNT
        buffer[8] = 0x00; buffer[9] = 0x00;
        buffer[10] = 0x00; buffer[11] = 0x00;

        // Дописуємо блок Resource Record (Answer) наприкінці секції Question:
        // Вказівник на ім'я QNAME: 0xC00C (зміщення 12 на початок імені в запиті)
        buffer[len++] = 0xC0;
        buffer[len++] = 0x0C;

        // TYPE: 0x0001 (A - IPv4)
        buffer[len++] = 0x00;
        buffer[len++] = 0x01;

        // CLASS: 0x0001 (IN - Internet)
        buffer[len++] = 0x00;
        buffer[len++] = 0x01;

        // TTL: 10 секунд (0x0000000A)
        buffer[len++] = 0x00;
        buffer[len++] = 0x00;
        buffer[len++] = 0x00;
        buffer[len++] = 0x0A;

        // RDLENGTH: 4 байти для адреси IPv4
        buffer[len++] = 0x00;
        buffer[len++] = 0x04;

        // RDATA: 192.168.4.1 (0xC0, 0xA8, 0x04, 0x01)
        buffer[len++] = 192;
        buffer[len++] = 168;
        buffer[len++] = 4;
        buffer[len++] = 1;

        sendto(sock, buffer, len, 0, (struct sockaddr *)&client_addr, client_len);
    }
}
