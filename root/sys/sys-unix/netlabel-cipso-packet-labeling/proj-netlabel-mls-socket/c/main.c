#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#define SERVER_PORT 8443
#define PEERSEC_BUF_SIZE 512

/*
 * Функція видобування контексту безпеки віддаленого піра через SO_PEERSEC.
 * Повертає 0 у разі успіху або від'ємний код помилки (-errno).
 */
static int get_peer_security_context(int sock_fd, char *buf, size_t buf_size) {
    socklen_t optlen = (socklen_t)buf_size;
    
    if (getsockopt(sock_fd, SOL_SOCKET, SO_PEERSEC, buf, &optlen) < 0) {
        return -errno;
    }
    
    /* Гарантуємо наявність нульового байта наприкінці рядка */
    if (optlen < buf_size) {
        buf[optlen] = '\0';
    } else {
        buf[buf_size - 1] = '\0';
    }
    return 0;
}

int main(void) {
    int server_fd = -1;
    int client_fd = -1;
    struct sockaddr_in server_addr;
    struct sockaddr_in client_addr;
    socklen_t client_len = sizeof(client_addr);
    char sec_context[PEERSEC_BUF_SIZE];
    int opt = 1;

    server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd < 0) {
        perror("Помилка створення сокета");
        return EXIT_FAILURE;
    }

    if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt)) < 0) {
        perror("Помилка setsockopt SO_REUSEADDR");
        close(server_fd);
        return EXIT_FAILURE;
    }

    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    server_addr.sin_port = htons(SERVER_PORT);

    if (bind(server_fd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        perror("Помилка прив'язки bind()");
        close(server_fd);
        return EXIT_FAILURE;
    }

    if (listen(server_fd, 10) < 0) {
        perror("Помилка переведення в режим listen()");
        close(server_fd);
        return EXIT_FAILURE;
    }

    printf("[INFO] MLS TCP-сервер очікує з'єднання на порту %d...\n", SERVER_PORT);

    while (1) {
        client_fd = accept(server_fd, (struct sockaddr *)&client_addr, &client_len);
        if (client_fd < 0) {
            if (errno == EINTR) continue;
            perror("Помилка accept()");
            break;
        }

        char client_ip[INET_ADDRSTRLEN];
        inet_ntop(AF_INET, &client_addr.sin_addr, client_ip, sizeof(client_ip));
        printf("\n[CONNECT] Отримано запит від %s:%d\n", client_ip, ntohs(client_addr.sin_port));

        memset(sec_context, 0, sizeof(sec_context));
        int res = get_peer_security_context(client_fd, sec_context, sizeof(sec_context));
        if (res == 0) {
            printf("[NETLABEL/LSM] SO_PEERSEC контекст клієнта: %s\n", sec_context);
        } else {
            if (res == -ENOPROTOOPT) {
                printf("[NETLABEL/LSM] SO_PEERSEC не підтримується модулем безпеки або немає мітки\n");
            } else {
                printf("[NETLABEL/LSM] Помилка отримання мітки: %s (код %d)\n", strerror(-res), -res);
            }
        }

        const char *response = "HTTP/1.1 200 OK\r\nContent-Length: 15\r\n\r\nMLS ACK RECEIVED";
        write(client_fd, response, strlen(response));

        close(client_fd);
        client_fd = -1;
    }

    close(server_fd);
    return EXIT_SUCCESS;
}
