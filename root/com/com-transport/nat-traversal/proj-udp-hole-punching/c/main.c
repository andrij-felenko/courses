#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <unistd.h>
#include <time.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <netdb.h>

#define STUN_MAGIC_COOKIE 0x2112A442
#define STUN_BINDING_REQ   0x0001
#define STUN_BINDING_RESP  0x0101
#define ATTR_XOR_MAPPED_ADDR 0x0020

#pragma pack(push, 1)
typedef struct {
    uint16_t msg_type;
    uint16_t msg_length;
    uint32_t magic_cookie;
    uint8_t  transaction_id[12];
} StunMsgHeader;

typedef struct {
    uint16_t type;
    uint16_t length;
} StunAttrHeader;
#pragma pack(pop)

/* Запит до STUN-сервера та вилучення публічного рефлексивного сокета */
int get_reflexive_address(int sockfd, const char *stun_host, uint16_t stun_port,
                          char *out_ip, uint16_t *out_port) {
    struct hostent *server = gethostbyname(stun_host);
    if (!server) {
        perror("gethostbyname");
        return -1;
    }

    struct sockaddr_in serv_addr;
    memset(&serv_addr, 0, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(stun_port);
    memcpy(&serv_addr.sin_addr.s_addr, server->h_addr_list[0], server->h_length);

    /* Формування заголовка Binding Request */
    StunMsgHeader req;
    req.msg_type = htons(STUN_BINDING_REQ);
    req.msg_length = htons(0);
    req.magic_cookie = htonl(STUN_MAGIC_COOKIE);
    for (int i = 0; i < 12; i++) {
        req.transaction_id[i] = (uint8_t)(rand() % 256);
    }

    /* Відправка STUN Binding Request */
    if (sendto(sockfd, &req, sizeof(req), 0, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0) {
        perror("sendto STUN");
        return -1;
    }

    uint8_t buf[512];
    struct sockaddr_in from_addr;
    socklen_t from_len = sizeof(from_addr);

    ssize_t n = recvfrom(sockfd, buf, sizeof(buf), 0, (struct sockaddr *)&from_addr, &from_len);
    if (n < (ssize_t)sizeof(StunMsgHeader)) {
        fprintf(stderr, "Помилка: занадто коротка відповідь STUN\n");
        return -1;
    }

    StunMsgHeader *resp = (StunMsgHeader *)buf;
    if (ntohs(resp->msg_type) != STUN_BINDING_RESP ||
        ntohl(resp->magic_cookie) != STUN_MAGIC_COOKIE ||
        memcmp(req.transaction_id, resp->transaction_id, 12) != 0) {
        fprintf(stderr, "Помилка валідації заголовка STUN або розбіжність Transaction ID\n");
        return -1;
    }

    /* Розбір TLV-атрибутів */
    uint16_t body_len = ntohs(resp->msg_length);
    size_t offset = sizeof(StunMsgHeader);
    size_t end = sizeof(StunMsgHeader) + body_len;

    while (offset + sizeof(StunAttrHeader) <= end && offset + sizeof(StunAttrHeader) <= (size_t)n) {
        StunAttrHeader *attr = (StunAttrHeader *)(buf + offset);
        uint16_t attr_type = ntohs(attr->type);
        uint16_t attr_len = ntohs(attr->length);
        offset += sizeof(StunAttrHeader);

        if (attr_type == ATTR_XOR_MAPPED_ADDR && attr_len >= 8) {
            uint8_t family = buf[offset + 1];
            if (family == 0x01) { /* IPv4 */
                uint16_t raw_xport;
                uint32_t raw_xaddr;
                memcpy(&raw_xport, buf + offset + 2, 2);
                memcpy(&raw_xaddr, buf + offset + 4, 4);

                uint16_t port = ntohs(raw_xport) ^ (STUN_MAGIC_COOKIE >> 16);
                uint32_t addr = ntohl(raw_xaddr) ^ STUN_MAGIC_COOKIE;

                struct in_addr in;
                in.s_addr = htonl(addr);
                strcpy(out_ip, inet_ntoa(in));
                *out_port = port;
                return 0;
            }
        }
        offset += (attr_len + 3) & ~3; /* Вирівнювання до 4 байтів */
    }

    return -1;
}

int main(int argc, char *argv[]) {
    srand(time(NULL));

    /* Створення єдиного сокета для всієї сесії */
    int sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sockfd < 0) {
        perror("socket");
        return 1;
    }

    struct sockaddr_in local_addr;
    memset(&local_addr, 0, sizeof(local_addr));
    local_addr.sin_family = AF_INET;
    local_addr.sin_addr.s_addr = INADDR_ANY;
    local_addr.sin_port = htons(50000);

    if (bind(sockfd, (struct sockaddr *)&local_addr, sizeof(local_addr)) < 0) {
        perror("bind");
        close(sockfd);
        return 1;
    }

    char pub_ip[64];
    uint16_t pub_port = 0;
    printf("[STUN] Визначення зовнішнього рефлексивного сокета через stun1.l.google.com:19302...\n");

    if (get_reflexive_address(sockfd, "stun1.l.google.com", 19302, pub_ip, &pub_port) == 0) {
        printf("[STUN] Успіх! Публічний рефлексивний сокет: %s:%u\n", pub_ip, pub_port);
    } else {
        fprintf(stderr, "[STUN] Не вдалося отримати рефлексивну адресу\n");
    }

    /* Виконання Hole Punching до віддаленого піра, якщо передано аргументи */
    if (argc >= 3) {
        const char *peer_ip = argv[1];
        uint16_t peer_port = (uint16_t)atoi(argv[2]);
        printf("[P2P] Початок UDP Hole Punching до цільового сокета %s:%u...\n", peer_ip, peer_port);

        struct sockaddr_in peer_addr;
        memset(&peer_addr, 0, sizeof(peer_addr));
        peer_addr.sin_family = AF_INET;
        peer_addr.sin_port = htons(peer_port);
        inet_pton(AF_INET, peer_ip, &peer_addr.sin_addr);

        const char *ping_msg = "HOLE_PUNCH_PING";
        for (int i = 0; i < 5; i++) {
            sendto(sockfd, ping_msg, strlen(ping_msg), 0, (struct sockaddr *)&peer_addr, sizeof(peer_addr));
            usleep(100000); /* 100 мс між спробами */
        }
        printf("[P2P] Серію пробних пакетів надіслано. Канал готовий для обміну даними.\n");
    }

    close(sockfd);
    return 0;
}
