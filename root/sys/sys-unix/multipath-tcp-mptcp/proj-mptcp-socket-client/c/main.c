/* MPTCP Client implementation in C (POSIX C99) */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

/* Резервні макроси для застарілих версій системних заголовків glibc */
#ifndef IPPROTO_MPTCP
#define IPPROTO_MPTCP 262
#endif

#ifndef SOL_MPTCP
#define SOL_MPTCP 284
#endif

#ifndef MPTCP_INFO
#define MPTCP_INFO 1
#endif

#define MPTCP_INFO_FLAG_FALLBACK 0x01

/* Сумісний буфер для зчитування ядерної структури mptcp_info */
struct mptcp_info_buffer {
    uint8_t  mptcpi_subflows;
    uint8_t  mptcpi_add_addr_accepted;
    uint8_t  mptcpi_subflows_max;
    uint8_t  mptcpi_add_addr_accepted_max;
    uint32_t mptcpi_flags;
    uint32_t mptcpi_token;
    uint32_t mptcpi_write_seq;
    uint32_t mptcpi_snd_una;
    uint32_t mptcpi_rcv_nxt;
};

static void print_mptcp_status(int sock_fd) {
    struct mptcp_info_buffer info;
    socklen_t len = sizeof(info);
    memset(&info, 0, sizeof(info));

    if (getsockopt(sock_fd, SOL_MPTCP, MPTCP_INFO, &info, &len) < 0) {
        perror("[!] getsockopt(SOL_MPTCP, MPTCP_INFO) failed");
        return;
    }

    printf("=========================================\n");
    printf("     ПОТОЧНИЙ СТАН MPTCP-МЕТА-СОКЕТА     \n");
    printf("=========================================\n");
    printf(" Токен з'єднання (Token)        : 0x%08x\n", info.mptcpi_token);
    printf(" Додаткових підпотоків (Subflows): %u\n", info.mptcpi_subflows);
    printf(" Прийнятих адрес (ADD_ADDR)     : %u\n", info.mptcpi_add_addr_accepted);
    
    if (info.mptcpi_flags & MPTCP_INFO_FLAG_FALLBACK) {
        printf(" Стан протоколу                : FALLBACK (Одношляховий TCP)\n");
    } else {
        printf(" Стан протоколу                : MULTIPATH TCP ACTIVE (Багатошляховий режим)\n");
    }
    printf("=========================================\n\n");
}

int main(int argc, char *argv[]) {
    const char *server_ip = (argc > 1) ? argv[1] : "127.0.0.1";
    uint16_t port = (argc > 2) ? (uint16_t)atoi(argv[2]) : 8080;
    int sockfd = -1;
    struct sockaddr_in serv_addr;
    const char *msg = "GET / HTTP/1.1\r\nHost: mptcp.test\r\nConnection: close\r\n\r\n";
    char response[512];
    ssize_t bytes;

    printf("[+] Створення мережевого сокета IPPROTO_MPTCP...\n");
    sockfd = socket(AF_INET, SOCK_STREAM, IPPROTO_MPTCP);
    if (sockfd < 0) {
        if (errno == EPROTONOSUPPORT || errno == ENOPROTOOPT) {
            fprintf(stderr, "[-] Ядро Linux не підтримує IPPROTO_MPTCP. Спроба створити звичайний TCP сокет...\n");
            sockfd = socket(AF_INET, SOCK_STREAM, IPPROTO_IP);
        }
        if (sockfd < 0) {
            perror("[-] Помилка створення сокета");
            return EXIT_FAILURE;
        }
    }

    memset(&serv_addr, 0, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(port);

    if (inet_pton(AF_INET, server_ip, &serv_addr.sin_addr) <= 0) {
        fprintf(stderr, "[-] Некоректний формат IP-адреси: %s\n", server_ip);
        close(sockfd);
        return EXIT_FAILURE;
    }

    printf("[+] Підключення до сервера %s:%u...\n", server_ip, port);
    if (connect(sockfd, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0) {
        perror("[-] Помилка підключення connect()");
        close(sockfd);
        return EXIT_FAILURE;
    }

    printf("[+] З'єднання успішно встановлено!\n");
    print_mptcp_status(sockfd);

    printf("[+] Надсилання HTTP-запиту...\n");
    if (send(sockfd, msg, strlen(msg), 0) < 0) {
        perror("[-] Помилка відправки send()");
    } else {
        bytes = recv(sockfd, response, sizeof(response) - 1, 0);
        if (bytes > 0) {
            response[bytes] = '\0';
            printf("[+] Отримано відповідь сервера (%zd байт):\n%s\n", bytes, response);
        }
    }

    print_mptcp_status(sockfd);

    close(sockfd);
    printf("[+] Сокет закрито. Завершення програми.\n");
    return EXIT_SUCCESS;
}
