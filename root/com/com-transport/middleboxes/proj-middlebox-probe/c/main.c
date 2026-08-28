#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <netinet/ip.h>
#include <netinet/tcp.h>
#include <sys/socket.h>
#include <sys/time.h>

#define PACKET_BUFFER_SIZE 4096
#define TEST_TCP_MSS 1460
#define EXPERIMENTAL_OPT_KIND 30 /* MPTCP option kind */

/* Псевдозаголовок для розрахунку контрольної суми TCP */
struct pseudo_header {
    uint32_t src_ip;
    uint32_t dst_ip;
    uint8_t  placeholder;
    uint8_t  protocol;
    uint16_t tcp_length;
};

/* Обчислення Інтернет-контрольної суми (RFC 1071) */
static uint16_t calculate_checksum(const uint16_t *addr, int count) {
    uint32_t sum = 0;
    while (count > 1) {
        sum += *addr++;
        count -= 2;
    }
    if (count > 0) {
        sum += *(const uint8_t *)addr;
    }
    while (sum >> 16) {
        sum = (sum & 0xFFFF) + (sum >> 16);
    }
    return (uint16_t)(~sum);
}

/* Формування та відправка сирого TCP SYN із нестандартними опціями */
int send_probe_syn(int raw_sock, const char *src_ip, const char *dst_ip,
                   uint16_t src_port, uint16_t dst_port, uint32_t isn) {
    char packet[PACKET_BUFFER_SIZE];
    memset(packet, 0, sizeof(packet));

    struct iphdr *iph = (struct iphdr *)packet;
    struct tcphdr *tcph = (struct tcphdr *)(packet + sizeof(struct iphdr));
    uint8_t *options = (uint8_t *)(packet + sizeof(struct iphdr) + sizeof(struct tcphdr));

    /* Додавання TCP Options */
    int opt_idx = 0;

    /* Опція 1: MSS (Kind=2, Length=4, Value=1460) */
    options[opt_idx++] = 2;
    options[opt_idx++] = 4;
    options[opt_idx++] = (TEST_TCP_MSS >> 8) & 0xFF;
    options[opt_idx++] = TEST_TCP_MSS & 0xFF;

    /* Опція 2: MPTCP (Kind=30, Length=4, Value=0xDEAD) */
    options[opt_idx++] = EXPERIMENTAL_OPT_KIND;
    options[opt_idx++] = 4;
    options[opt_idx++] = 0xDE;
    options[opt_idx++] = 0xAD;

    /* Вирівнювання заголовка TCP до кратності 4 байтам (NOP + EOL) */
    options[opt_idx++] = 1; /* NOP */
    options[opt_idx++] = 0; /* EOL */
    while (opt_idx % 4 != 0) {
        options[opt_idx++] = 0;
    }

    int tcp_hdr_len = sizeof(struct tcphdr) + opt_idx;
    int total_len = sizeof(struct iphdr) + tcp_hdr_len;

    /* Заповнення полів IPv4 */
    iph->ihl = 5;
    iph->version = 4;
    iph->tos = 0;
    iph->tot_len = htons((uint16_t)total_len);
    iph->id = htons(54321);
    iph->frag_off = htons(0x4000); /* DF bit */
    iph->ttl = 64;
    iph->protocol = IPPROTO_TCP;
    iph->saddr = inet_addr(src_ip);
    iph->daddr = inet_addr(dst_ip);
    iph->check = calculate_checksum((uint16_t *)iph, sizeof(struct iphdr));

    /* Заповнення полів TCP */
    tcph->source = htons(src_port);
    tcph->dest = htons(dst_port);
    tcph->seq = htonl(isn);
    tcph->ack_seq = 0;
    tcph->doff = (uint8_t)(tcp_hdr_len / 4);
    tcph->syn = 1;
    tcph->window = htons(65535);
    tcph->check = 0;
    tcph->urg_ptr = 0;

    /* Розрахунок контрольної суми TCP з псевдозаголовком */
    struct pseudo_header psh;
    psh.src_ip = iph->saddr;
    psh.dst_ip = iph->daddr;
    psh.placeholder = 0;
    psh.protocol = IPPROTO_TCP;
    psh.tcp_length = htons((uint16_t)tcp_hdr_len);

    char pseudo_block[PACKET_BUFFER_SIZE];
    memcpy(pseudo_block, &psh, sizeof(struct pseudo_header));
    memcpy(pseudo_block + sizeof(struct pseudo_header), tcph, tcp_hdr_len);

    tcph->check = calculate_checksum((uint16_t *)pseudo_block,
                                     sizeof(struct pseudo_header) + tcp_hdr_len);

    struct sockaddr_in sin;
    memset(&sin, 0, sizeof(sin));
    sin.sin_family = AF_INET;
    sin.sin_port = htons(dst_port);
    sin.sin_addr.s_addr = iph->daddr;

    if (sendto(raw_sock, packet, total_len, 0,
               (struct sockaddr *)&sin, sizeof(sin)) < 0) {
        perror("Помилка sendto raw_sock");
        return -1;
    }

    printf("[PROBE] SYN надіслано до %s:%u (ISN=%u, MSS=%u, OptKind=%u)\n",
           dst_ip, dst_port, isn, TEST_TCP_MSS, EXPERIMENTAL_OPT_KIND);
    return 0;
}

/* Отримання та аналіз відповіді SYN-ACK */
int listen_and_analyze(int raw_sock, const char *expected_src, uint16_t expected_port, uint32_t sent_isn) {
    char buffer[PACKET_BUFFER_SIZE];
    struct timeval tv = { .tv_sec = 3, .tv_usec = 0 };
    setsockopt(raw_sock, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));

    while (1) {
        ssize_t len = recvfrom(raw_sock, buffer, sizeof(buffer), 0, NULL, NULL);
        if (len < 0) {
            printf("[TIMEOUT] Не отримано відповіді протягом 3 секунд (можливе блокування middlebox)\n");
            return -1;
        }

        struct iphdr *iph = (struct iphdr *)buffer;
        if (iph->protocol != IPPROTO_TCP) continue;

        int ip_hdr_len = iph->ihl * 4;
        if (len < ip_hdr_len + (int)sizeof(struct tcphdr)) continue;

        struct tcphdr *tcph = (struct tcphdr *)(buffer + ip_hdr_len);
        struct in_addr src_addr = { .s_addr = iph->saddr };

        if (strcmp(inet_ntoa(src_addr), expected_src) == 0 &&
            ntohs(tcph->source) == expected_port) {

            printf("\n--- РЕЗУЛЬТАТ АНАЛІЗУ СИРОГО ПАКЕТА ВІДПОВІДІ ---\n");
            printf("Прапорці TCP: %s%s\n", tcph->syn ? "SYN " : "", tcph->ack ? "ACK " : "");
            
            uint32_t recv_ack = ntohl(tcph->ack_seq);
            printf("Acknowledgment Number: %u (Очікувалось: %u)\n", recv_ack, sent_isn + 1);
            if (recv_ack != sent_isn + 1) {
                printf("  [!] ВИЯВЛЕНО ПІДМІНУ ISN / СЕКВЕНЦІЇ транзитним пристроєм!\n");
            } else {
                printf("  [OK] Номер підтвердження узгоджено коректно.\n");
            }

            int tcp_hdr_len = tcph->doff * 4;
            int opt_len = tcp_hdr_len - (int)sizeof(struct tcphdr);

            if (opt_len > 0) {
                const uint8_t *opts = (const uint8_t *)(buffer + ip_hdr_len + sizeof(struct tcphdr));
                int i = 0;
                int found_experimental = 0;

                while (i < opt_len) {
                    uint8_t kind = opts[i];
                    if (kind == 0) break; /* EOL */
                    if (kind == 1) { i++; continue; } /* NOP */

                    if (i + 1 >= opt_len) break;
                    uint8_t length = opts[i + 1];
                    if (length < 2 || i + length > opt_len) break;

                    if (kind == 2 && length == 4) {
                        uint16_t mss = (opts[i + 2] << 8) | opts[i + 3];
                        printf("Опція MSS у відповіді: %u\n", mss);
                    } else if (kind == EXPERIMENTAL_OPT_KIND) {
                        found_experimental = 1;
                        printf("  [OK] Експериментальну опцію (Kind=%u) пропущено мережею!\n", kind);
                    }
                    i += length;
                }

                if (!found_experimental) {
                    printf("  [!] Експериментальну опцію Kind=%u НЕ виявлено у відповіді (Option Stripping).\n",
                           EXPERIMENTAL_OPT_KIND);
                }
            } else {
                printf("  [!] Усі опції TCP видалено із заголовка відповіді.\n");
            }
            return 0;
        }
    }
}

int main(int argc, char *argv[]) {
    if (argc < 5) {
        fprintf(stderr, "Використання: %s <src_ip> <dst_ip> <src_port> <dst_port>\n", argv[0]);
        return 1;
    }

    int raw_sock = socket(AF_INET, SOCK_RAW, IPPROTO_RAW);
    if (raw_sock < 0) {
        perror("Потрібні права root / CAP_NET_RAW для створення SOCK_RAW");
        return 1;
    }

    int one = 1;
    if (setsockopt(raw_sock, IPPROTO_IP, IP_HDRINCL, &one, sizeof(one)) < 0) {
        perror("Помилка IP_HDRINCL");
        close(raw_sock);
        return 1;
    }

    uint16_t src_port = (uint16_t)atoi(argv[3]);
    uint16_t dst_port = (uint16_t)atoi(argv[4]);
    uint32_t probe_isn = 0x12345678;

    if (send_probe_syn(raw_sock, argv[1], argv[2], src_port, dst_port, probe_isn) == 0) {
        /* Для читання потрібен сокет з IPPROTO_TCP */
        int recv_sock = socket(AF_INET, SOCK_RAW, IPPROTO_TCP);
        if (recv_sock >= 0) {
            listen_and_analyze(recv_sock, argv[2], dst_port, probe_isn);
            close(recv_sock);
        }
    }

    close(raw_sock);
    return 0;
}
