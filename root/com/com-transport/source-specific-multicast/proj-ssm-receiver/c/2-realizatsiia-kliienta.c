#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>

#define MCAST_PORT 5004
#define MCAST_ADDR "232.1.1.1"
#define SOURCE_ADDR "198.51.100.1"
#define IFACE_ADDR  "192.0.2.50"
#define BUFFER_SIZE 2048

int main(void) {
    int sock_fd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sock_fd < 0) {
        perror("Помилка створення сокета");
        return EXIT_FAILURE;
    }

    int reuse = 1;
    if (setsockopt(sock_fd, SOL_SOCKET, SO_REUSEADDR, &reuse, sizeof(reuse)) < 0) {
        perror("Помилка встановлення SO_REUSEADDR");
        close(sock_fd);
        return EXIT_FAILURE;
    }

    struct sockaddr_in bind_addr;
    memset(&bind_addr, 0, sizeof(bind_addr));
    bind_addr.sin_family = AF_INET;
    bind_addr.sin_port = htons(MCAST_PORT);
    bind_addr.sin_addr.s_addr = htonl(INADDR_ANY);

    if (bind(sock_fd, (struct sockaddr *)&bind_addr, sizeof(bind_addr)) < 0) {
        perror("Помилка прив'язки bind()");
        close(sock_fd);
        return EXIT_FAILURE;
    }

    /* Налаштування фільтрації за джерелом: приєднуємося до (S, G) */
    struct ip_mreq_source mreq;
    memset(&mreq, 0, sizeof(mreq));
    inet_pton(AF_INET, MCAST_ADDR, &mreq.imr_multiaddr);
    inet_pton(AF_INET, SOURCE_ADDR, &mreq.imr_sourceaddr);
    inet_pton(AF_INET, IFACE_ADDR, &mreq.imr_interface);

    if (setsockopt(sock_fd, IPPROTO_IP, IP_ADD_SOURCE_MEMBERSHIP, &mreq, sizeof(mreq)) < 0) {
        perror("Помилка IP_ADD_SOURCE_MEMBERSHIP");
        close(sock_fd);
        return EXIT_FAILURE;
    }

    printf("Успішно підписано на SSM канал (%s, %s) через інтерфейс %s\n",
           SOURCE_ADDR, MCAST_ADDR, IFACE_ADDR);

    char buffer[BUFFER_SIZE];
    struct sockaddr_in sender_addr;
    socklen_t addr_len = sizeof(sender_addr);

    while (1) {
        ssize_t received = recvfrom(sock_fd, buffer, sizeof(buffer) - 1, 0,
                                    (struct sockaddr *)&sender_addr, &addr_len);
        if (received < 0) {
            perror("Помилка читання recvfrom()");
            break;
        }

        buffer[received] = '\0';
        char sender_ip[INET_ADDRSTRLEN];
        inet_ntop(AF_INET, &sender_addr.sin_addr, sender_ip, sizeof(sender_ip));

        printf("Отримано %zd байтів від %s:%d -> %s\n",
               received, sender_ip, ntohs(sender_addr.sin_port), buffer);
    }

    /* Коректне відключення від каналу */
    setsockopt(sock_fd, IPPROTO_IP, IP_DROP_SOURCE_MEMBERSHIP, &mreq, sizeof(mreq));
    close(sock_fd);
    return EXIT_SUCCESS;
}
