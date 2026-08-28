/* pmtu_probe.c — Активне зондування Path MTU мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/ip.h>
#include <netinet/ip_icmp.h>
#include <arpa/inet.h>
#include <sys/time.h>

#define MIN_MTU 576
#define MAX_MTU 9000
#define TIMEOUT_SEC 1

/* Обчислення контрольної суми Інтернету (RFC 1071) */
static unsigned short checksum(void *b, int len) {
    unsigned short *buf = (unsigned short *)b;
    unsigned int sum = 0;
    unsigned short result;

    for (sum = 0; len > 1; len -= 2) {
        sum += *buf++;
    }
    if (len == 1) {
        sum += *(unsigned char *)buf;
    }
    sum = (sum >> 16) + (sum & 0xFFFF);
    sum += (sum >> 16);
    result = (unsigned short)(~sum);
    return result;
}

/* Відправка одного ICMP-зонда із забороною фрагментації */
static int probe_size(int sock, struct sockaddr_in *dst, int total_ip_size) {
    /* 20 байтів IP-заголовок, 8 байтів ICMP-заголовок */
    int icmp_payload_len = total_ip_size - 20 - 8;
    if (icmp_payload_len < 0) return 0;

    int packet_len = sizeof(struct icmphdr) + icmp_payload_len;
    char *packet = (char *)malloc(packet_len);
    if (!packet) return 0;

    /* Заповнення тіла запиту детермінованим шаблоном */
    memset(packet, 0x41, packet_len);

    struct icmphdr *icmp = (struct icmphdr *)packet;
    icmp->type = ICMP_ECHO;
    icmp->code = 0;
    icmp->un.echo.id = htons((unsigned short)(getpid() & 0xFFFF));
    icmp->un.echo.sequence = htons((unsigned short)total_ip_size);
    icmp->checksum = 0;
    icmp->checksum = checksum(packet, packet_len);

    ssize_t sent = sendto(sock, packet, packet_len, 0,
                          (struct sockaddr *)dst, sizeof(*dst));
    free(packet);

    if (sent < 0) {
        if (errno == EMSGSIZE) {
            /* Локальне ядро заблокувало пакет: розмір більший за MTU адаптера */
            return -1;
        }
        return 0;
    }

    /* Очікування відповіді з таймаутом */
    char recv_buf[2048];
    struct sockaddr_in from;
    socklen_t from_len = sizeof(from);

    ssize_t received = recvfrom(sock, recv_buf, sizeof(recv_buf), 0,
                                (struct sockaddr *)&from, &from_len);
    if (received < 0) {
        /* Тайм-аут: пакет скинуто проміжним вузлом (Black Hole) */
        return 0;
    }

    struct iphdr *ip_reply = (struct iphdr *)recv_buf;
    int ip_hdr_len = ip_reply->ihl * 4;
    if (received < ip_hdr_len + (int)sizeof(struct icmphdr)) {
        return 0;
    }

    struct icmphdr *icmp_reply = (struct icmphdr *)(recv_buf + ip_hdr_len);

    /* Перевірка валідності відповіді нашого процесу */
    if (icmp_reply->type == ICMP_ECHOREPLY &&
        icmp_reply->un.echo.id == htons((unsigned short)(getpid() & 0xFFFF))) {
        return 1; /* Успіх: пакет пройшов увесь тракт туди й назад */
    }

    return 0;
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Використання: %s <IP-адреса>\n", argv[0]);
        return 1;
    }

    int sock = socket(AF_INET, SOCK_RAW, IPPROTO_ICMP);
    if (sock < 0) {
        perror("Помилка створення raw socket (потрібні права root або CAP_NET_RAW)");
        return 1;
    }

    /* Примусове встановлення прапорця DF у ядрі Linux */
    int val = IP_PMTUDISC_DO;
    if (setsockopt(sock, IPPROTO_IP, IP_MTU_DISCOVER, &val, sizeof(val)) < 0) {
        perror("Помилка конфігурації IP_MTU_DISCOVER");
        close(sock);
        return 1;
    }

    /* Встановлення таймауту очікування відповіді на сокеті */
    struct timeval tv = { .tv_sec = TIMEOUT_SEC, .tv_usec = 0 };
    setsockopt(sock, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));

    struct sockaddr_in dst;
    memset(&dst, 0, sizeof(dst));
    dst.sin_family = AF_INET;
    if (inet_pton(AF_INET, argv[1], &dst.sin_addr) <= 0) {
        fprintf(stderr, "Некоректна IP-адреса призначення: %s\n", argv[1]);
        close(sock);
        return 1;
    }

    printf("Початок активного бінарного зондування Path MTU до %s...\n", argv[1]);

    int low = MIN_MTU;
    int high = MAX_MTU;
    int optimal_mtu = 0;
    int iterations = 0;

    while (low <= high) {
        iterations++;
        int mid = low + (high - low) / 2;
        printf("  [Ітерація %2d] Тестування розміру IP-пакета: %4d байтів... ", iterations, mid);
        fflush(stdout);

        int res = probe_size(sock, &dst, mid);
        if (res == 1) {
            printf("УСПІХ (OK)\n");
            optimal_mtu = mid;
            low = mid + 1; /* Звужуємо пошук у бік більших розмірів */
        } else {
            printf("ВІДМОВА (Drop / Local EMSGSIZE)\n");
            high = mid - 1; /* Звужуємо пошук у бік менших розмірів */
        }
    }

    printf("\n=== Підсумкові результати сканування ===\n");
    if (optimal_mtu > 0) {
        printf("Точний Path MTU каналу : %d байтів\n", optimal_mtu);
        printf("Безпечний IPv4 TCP MSS : %d байтів (MTU - 40)\n", optimal_mtu - 40);
        printf("Безпечний IPv6 TCP MSS : %d байтів (MTU - 60)\n", optimal_mtu - 60);
    } else {
        printf("Помилка: цільовий вузол повністю недосяжний або блокує всі ICMP-пакети.\n");
    }

    close(sock);
    return 0;
}
