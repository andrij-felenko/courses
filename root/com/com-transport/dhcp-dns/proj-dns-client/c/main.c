#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <time.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <sys/time.h>

#define DNS_PORT 53
#define BUFFER_SIZE 512
#define MAX_LABEL_LEN 63
#define MAX_HOPS 16

/* 12-байтний заголовок DNS за стандартом RFC 1035 */
#pragma pack(push, 1)
typedef struct {
    uint16_t id;
    uint16_t flags;
    uint16_t qdcount;
    uint16_t ancount;
    uint16_t nscount;
    uint16_t arcount;
} dns_header_t;
#pragma pack(pop)

/* Перетворення рядка "example.com" у формат міток DNS "\x07example\x03com\x00" */
static int encode_dns_name(const char *hostname, uint8_t *buffer, size_t max_len) {
    size_t host_len = strlen(hostname);
    if (host_len + 2 > max_len) return -1;

    uint8_t *out = buffer;
    const char *start = hostname;
    const char *dot;

    while ((dot = strchr(start, '.')) != NULL) {
        size_t label_len = (size_t)(dot - start);
        if (label_len == 0 || label_len > MAX_LABEL_LEN) return -1;

        *out++ = (uint8_t)label_len;
        memcpy(out, start, label_len);
        out += label_len;
        start = dot + 1;
    }

    size_t last_len = strlen(start);
    if (last_len > 0) {
        if (last_len > MAX_LABEL_LEN) return -1;
        *out++ = (uint8_t)last_len;
        memcpy(out, start, last_len);
        out += last_len;
    }

    *out++ = 0x00; /* Корінь DNS */
    return (int)(out - buffer);
}

/* Декодування стисненого або відкритого імені DNS із буфера відповіді */
static int parse_dns_name(const uint8_t *packet, size_t packet_len, size_t offset,
                          char *out_name, size_t out_max, size_t *bytes_consumed) {
    size_t curr = offset;
    size_t out_idx = 0;
    int hops = 0;
    bool jumped = false;
    size_t initial_bytes = 0;

    while (curr < packet_len && hops < MAX_HOPS) {
        uint8_t len = packet[curr];

        if (len == 0) { /* Завершення імені */
            if (!jumped) initial_bytes = (curr - offset) + 1;
            curr++;
            break;
        }

        if ((len & 0xC0) == 0xC0) { /* Покажчик компресії */
            if (curr + 1 >= packet_len) return -1;
            uint16_t ptr_offset = (uint16_t)(((len & 0x3F) << 8) | packet[curr + 1]);
            if (ptr_offset >= packet_len) return -1;

            if (!jumped) {
                initial_bytes = (curr - offset) + 2;
                jumped = true;
            }
            curr = ptr_offset;
            hops++;
            continue;
        }

        /* Звичайна текстова мітка */
        curr++;
        if (curr + len > packet_len) return -1;
        if (out_idx + len + 2 > out_max) return -1;

        if (out_idx > 0) out_name[out_idx++] = '.';
        memcpy(&out_name[out_idx], &packet[curr], len);
        out_idx += len;
        curr += len;

        if (!jumped) initial_bytes = curr - offset;
    }

    if (hops >= MAX_HOPS) return -1; /* Захист від зациклення */
    out_name[out_idx] = '\0';
    if (bytes_consumed) *bytes_consumed = initial_bytes;
    return 0;
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Ужиток: %s <доменне ім'я> [DNS сервер]\n", argv[0]);
        return 1;
    }

    const char *hostname = argv[1];
    const char *dns_server = (argc >= 3) ? argv[2] : "8.8.8.8";

    printf("Розв'язання імені '%s' через DNS-сервер %s...\n", hostname, dns_server);

    /* 1. Створення сокета UDP */
    int sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sockfd < 0) {
        perror("Помилка створення сокета");
        return 1;
    }

    /* Встановлення таймауту отримання 3 секунди */
    struct timeval tv = { .tv_sec = 3, .tv_usec = 0 };
    setsockopt(sockfd, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));

    struct sockaddr_in serv_addr;
    memset(&serv_addr, 0, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(DNS_PORT);
    if (inet_pton(AF_INET, dns_server, &serv_addr.sin_addr) <= 0) {
        fprintf(stderr, "Некоректна IP-адреса DNS-сервера: %s\n", dns_server);
        close(sockfd);
        return 1;
    }

    /* 2. Формування пакета запиту */
    uint8_t packet[BUFFER_SIZE];
    memset(packet, 0, sizeof(packet));

    srand((unsigned)time(NULL) ^ getpid());
    uint16_t query_id = (uint16_t)(rand() & 0xFFFF);

    dns_header_t *hdr = (dns_header_t *)packet;
    hdr->id = htons(query_id);
    hdr->flags = htons(0x0100); /* RD = 1 (Recursion Desired) */
    hdr->qdcount = htons(1);

    size_t offset = sizeof(dns_header_t);
    int name_len = encode_dns_name(hostname, &packet[offset], sizeof(packet) - offset);
    if (name_len < 0) {
        fprintf(stderr, "Помилка кодування доменного імені\n");
        close(sockfd);
        return 1;
    }
    offset += (size_t)name_len;

    /* QTYPE = 1 (A), QCLASS = 1 (IN) */
    *(uint16_t *)(&packet[offset]) = htons(1);
    offset += 2;
    *(uint16_t *)(&packet[offset]) = htons(1);
    offset += 2;

    /* 3. Надсилання дейтаграми */
    ssize_t sent = sendto(sockfd, packet, offset, 0, (struct sockaddr *)&serv_addr, sizeof(serv_addr));
    if (sent < 0) {
        perror("Помилка надсилання запиту");
        close(sockfd);
        return 1;
    }

    /* 4. Отримання відповіді */
    uint8_t resp[BUFFER_SIZE];
    socklen_t addr_len = sizeof(serv_addr);
    ssize_t resp_len = recvfrom(sockfd, resp, sizeof(resp), 0, (struct sockaddr *)&serv_addr, &addr_len);
    if (resp_len < (ssize_t)sizeof(dns_header_t)) {
        fprintf(stderr, "Таймаут відповіді або отримано пошкоджений пакет\n");
        close(sockfd);
        return 1;
    }
    close(sockfd);

    /* 5. Перевірка заголовка відповіді */
    dns_header_t *resp_hdr = (dns_header_t *)resp;
    uint16_t resp_id = ntohs(resp_hdr->id);
    uint16_t flags = ntohs(resp_hdr->flags);
    uint16_t ancount = ntohs(resp_hdr->ancount);
    uint16_t qdcount = ntohs(resp_hdr->qdcount);

    if (resp_id != query_id) {
        fprintf(stderr, "Невідповідність Transaction ID (очікувалось 0x%04X, отримано 0x%04X)\n", query_id, resp_id);
        return 1;
    }

    uint8_t rcode = (uint8_t)(flags & 0x000F);
    if (rcode != 0) {
        fprintf(stderr, "Сервер повернув помилку DNS RCODE = %d (3 = NXDomain, 2 = ServFail)\n", rcode);
        return 1;
    }

    printf("Отримано успішну відповідь: записів у секції Answer = %d\n", ancount);

    /* 6. Пропуск секції Question */
    size_t curr = sizeof(dns_header_t);
    for (int q = 0; q < qdcount; q++) {
        char qname[256];
        size_t consumed = 0;
        if (parse_dns_name(resp, (size_t)resp_len, curr, qname, sizeof(qname), &consumed) < 0) {
            fprintf(stderr, "Помилка розбору секції Question\n");
            return 1;
        }
        curr += consumed + 4; /* Ім'я + QTYPE (2B) + QCLASS (2B) */
    }

    /* 7. Розбір секції Answer */
    for (int a = 0; a < ancount; a++) {
        if (curr >= (size_t)resp_len) break;

        char rr_name[256];
        size_t consumed = 0;
        if (parse_dns_name(resp, (size_t)resp_len, curr, rr_name, sizeof(rr_name), &consumed) < 0) {
            fprintf(stderr, "Помилка розбору імені в записі Answer #%d\n", a + 1);
            return 1;
        }
        curr += consumed;

        if (curr + 10 > (size_t)resp_len) break;
        uint16_t rtype = ntohs(*(uint16_t *)(&resp[curr]));
        uint16_t rclass = ntohs(*(uint16_t *)(&resp[curr + 2]));
        uint32_t ttl = ntohl(*(uint32_t *)(&resp[curr + 4]));
        uint16_t rdlength = ntohs(*(uint16_t *)(&resp[curr + 8]));
        curr += 10;

        if (curr + rdlength > (size_t)resp_len) break;

        if (rtype == 1 && rclass == 1 && rdlength == 4) { /* Запис типу A (IPv4) */
            char ip_str[INET_ADDRSTRLEN];
            inet_ntop(AF_INET, &resp[curr], ip_str, sizeof(ip_str));
            printf("  [A] %s -> %s (TTL: %u с)\n", rr_name, ip_str, ttl);
        } else if (rtype == 5) { /* Запис типу CNAME */
            char cname[256];
            if (parse_dns_name(resp, (size_t)resp_len, curr, cname, sizeof(cname), NULL) == 0) {
                printf("  [CNAME] %s -> псевдонім для %s (TTL: %u с)\n", rr_name, cname, ttl);
            }
        }
        curr += rdlength;
    }

    return 0;
}
