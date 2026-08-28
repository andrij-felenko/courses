#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <time.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <netinet/ip.h>
#include <netinet/ip_icmp.h>
#include <arpa/inet.h>

#define MAX_HOPS 30
#define TIMEOUT_MS 1000

/* Обчислення 16-бітної контрольної суми Internet Checksum (RFC 1071) */
static unsigned short compute_checksum(const void *data, size_t len) {
    const unsigned short *ptr = (const unsigned short *)data;
    unsigned int sum = 0;
    while (len > 1) {
        sum += *ptr++;
        len -= 2;
    }
    if (len == 1) {
        sum += *(const unsigned char *)ptr;
    }
    sum = (sum >> 16) + (sum & 0xFFFF);
    sum += (sum >> 16);
    return (unsigned short)(~sum);
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Використання: %s <IPv4-адреса>\n", argv[0]);
        return EXIT_FAILURE;
    }

    struct sockaddr_in target_addr;
    memset(&target_addr, 0, sizeof(target_addr));
    target_addr.sin_family = AF_INET;
    if (inet_pton(AF_INET, argv[1], &target_addr.sin_addr) <= 0) {
        perror("Некоректна IPv4-адреса");
        return EXIT_FAILURE;
    }

    /* Відкриття сирого сокета для протоколу ICMP */
    int sockfd = socket(AF_INET, SOCK_RAW, IPPROTO_ICMP);
    if (sockfd < 0) {
        perror("Помилка створення SOCK_RAW (потрібен привілей CAP_NET_RAW)");
        return EXIT_FAILURE;
    }

    /* Встановлення таймауту очікування на сокеті */
    struct timeval tv;
    tv.tv_sec = TIMEOUT_MS / 1000;
    tv.tv_usec = (TIMEOUT_MS % 1000) * 1000;
    if (setsockopt(sockfd, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv)) < 0) {
        perror("setsockopt(SO_RCVTIMEO)");
        close(sockfd);
        return EXIT_FAILURE;
    }

    uint16_t pid_ident = (uint16_t)(getpid() & 0xFFFF);
    printf("Трасування маршруту до %s (максимум %d хопів):\n", argv[1], MAX_HOPS);

    for (int ttl = 1; ttl <= MAX_HOPS; ++ttl) {
        /* Налаштування поля TTL у заголовку вихідного IP-пакета */
        if (setsockopt(sockfd, IPPROTO_IP, IP_TTL, &ttl, sizeof(ttl)) < 0) {
            perror("setsockopt(IP_TTL)");
            break;
        }

        /* Підготовка пакета ICMP Echo Request */
        struct icmphdr icmp_req;
        memset(&icmp_req, 0, sizeof(icmp_req));
        icmp_req.type = ICMP_ECHO;
        icmp_req.code = 0;
        icmp_req.un.echo.id = htons(pid_ident);
        icmp_req.un.echo.sequence = htons((uint16_t)ttl);
        icmp_req.checksum = compute_checksum(&icmp_req, sizeof(icmp_req));

        struct timespec start_ts, end_ts;
        clock_gettime(CLOCK_MONOTONIC, &start_ts);

        ssize_t sent = sendto(sockfd, &icmp_req, sizeof(icmp_req), 0,
                              (struct sockaddr *)&target_addr, sizeof(target_addr));
        if (sent < 0) {
            perror("sendto");
            break;
        }

        /* Очікування та обробка відповіді від мережі */
        unsigned char recv_buf[512];
        struct sockaddr_in reply_addr;
        socklen_t addr_len = sizeof(reply_addr);

        ssize_t received = recvfrom(sockfd, recv_buf, sizeof(recv_buf), 0,
                                    (struct sockaddr *)&reply_addr, &addr_len);
        clock_gettime(CLOCK_MONOTONIC, &end_ts);

        if (received < 0) {
            if (errno == EAGAIN || errno == EWOULDBLOCK) {
                printf("%2d  * * * (таймаут вузла)\n", ttl);
                continue;
            }
            perror("recvfrom");
            break;
        }

        double rtt_ms = (double)(end_ts.tv_sec - start_ts.tv_sec) * 1000.0 +
                        (double)(end_ts.tv_nsec - start_ts.tv_nsec) / 1000000.0;

        if (received < (ssize_t)sizeof(struct iphdr)) {
            continue;
        }

        struct iphdr *ip_hdr = (struct iphdr *)recv_buf;
        size_t ip_hdr_len = (size_t)(ip_hdr->ihl * 4);
        if (received < (ssize_t)(ip_hdr_len + sizeof(struct icmphdr))) {
            continue;
        }

        struct icmphdr *icmp_reply = (struct icmphdr *)(recv_buf + ip_hdr_len);
        char ip_str[INET_ADDRSTRLEN];
        inet_ntop(AF_INET, &reply_addr.sin_addr, ip_str, sizeof(ip_str));

        if (icmp_reply->type == ICMP_TIME_EXCEEDED && icmp_reply->code == 0) {
            /* Проміжний маршрутизатор */
            printf("%2d  %-15s  %.3f ms\n", ttl, ip_str, rtt_ms);
        } else if (icmp_reply->type == ICMP_ECHOREPLY) {
            /* Кінцевий цільовий вузол */
            printf("%2d  %-15s  %.3f ms (досягнуто призначення)\n", ttl, ip_str, rtt_ms);
            break;
        } else {
            printf("%2d  %-15s  ICMP type=%d code=%d  %.3f ms\n",
                   ttl, ip_str, icmp_reply->type, icmp_reply->code, rtt_ms);
        }
    }

    close(sockfd);
    return EXIT_SUCCESS;
}
