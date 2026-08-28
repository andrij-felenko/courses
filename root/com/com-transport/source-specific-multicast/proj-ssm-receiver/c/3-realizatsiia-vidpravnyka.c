#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <time.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>

#define MCAST_PORT 5004
#define MCAST_ADDR "232.1.1.1"
#define IFACE_ADDR "198.51.100.1"

int main(void) {
    int sock_fd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sock_fd < 0) {
        perror("Помилка створення сокета");
        return EXIT_FAILURE;
    }

    /* Вказуємо вихідний інтерфейс */
    struct in_addr iface;
    inet_pton(AF_INET, IFACE_ADDR, &iface);
    if (setsockopt(sock_fd, IPPROTO_IP, IP_MULTICAST_IF, &iface, sizeof(iface)) < 0) {
        perror("Помилка IP_MULTICAST_IF");
        close(sock_fd);
        return EXIT_FAILURE;
    }

    /* Встановлюємо TTL для проходження через маршрутизатори */
    unsigned char ttl = 16;
    if (setsockopt(sock_fd, IPPROTO_IP, IP_MULTICAST_TTL, &ttl, sizeof(ttl)) < 0) {
        perror("Помилка IP_MULTICAST_TTL");
        close(sock_fd);
        return EXIT_FAILURE;
    }

    struct sockaddr_in target_addr;
    memset(&target_addr, 0, sizeof(target_addr));
    target_addr.sin_family = AF_INET;
    target_addr.sin_port = htons(MCAST_PORT);
    inet_pton(AF_INET, MCAST_ADDR, &target_addr.sin_addr);

    printf("Початок мовлення у SSM групу %s:%d з інтерфейсу %s...\n",
           MCAST_ADDR, MCAST_PORT, IFACE_ADDR);

    int counter = 0;
    char payload[256];

    while (1) {
        snprintf(payload, sizeof(payload), "SSM_STREAM_PACKET #%d [Time=%ld]", ++counter, time(NULL));
        ssize_t sent = sendto(sock_fd, payload, strlen(payload), 0,
                              (struct sockaddr *)&target_addr, sizeof(target_addr));
        if (sent < 0) {
            perror("Помилка sendto()");
            break;
        }

        printf("Надіслано пакет #%d (%zd байтів)\n", counter, sent);
        sleep(1);
    }

    close(sock_fd);
    return EXIT_SUCCESS;
}
