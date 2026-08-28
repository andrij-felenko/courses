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
#include <poll.h>

#define BUFFER_SIZE 4096

/* Функція клієнта: передача потоку, напівзакриття та очікування звіту */
int run_half_close_client(const char *server_ip, int port) {
    int fd = socket(AF_INET, SOCK_STREAM, 0);
    if (fd < 0) {
        perror("socket");
        return -1;
    }

    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons((uint16_t)port);
    if (inet_pton(AF_INET, server_ip, &addr.sin_addr) <= 0) {
        perror("inet_pton");
        close(fd);
        return -1;
    }

    if (connect(fd, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        perror("connect");
        close(fd);
        return -1;
    }

    /* 1. Потокова передача повідомлень довільної довжини */
    const char *payloads[] = {
        "LOG_ENTRY: 2026-08-18 10:00:01 Node initialized\n",
        "LOG_ENTRY: 2026-08-18 10:00:02 Subsystems verified\n",
        "LOG_ENTRY: 2026-08-18 10:00:03 Telemetry stream active\n",
        NULL
    };

    for (int i = 0; payloads[i] != NULL; ++i) {
        size_t len = strlen(payloads[i]);
        ssize_t sent = write(fd, payloads[i], len);
        if (sent < 0) {
            perror("write");
            close(fd);
            return -1;
        }
    }

    /* 2. Напівзакриття: сигналізуємо серверу про завершення потоку відправки (FIN) */
    if (shutdown(fd, SHUT_WR) < 0) {
        perror("shutdown SHUT_WR");
        close(fd);
        return -1;
    }

    /* 3. Читання підсумкового звіту від сервера з відкритого вхідного каналу */
    char buf[BUFFER_SIZE];
    ssize_t n;
    while ((n = read(fd, buf, sizeof(buf) - 1)) > 0) {
        buf[n] = '\0';
        printf("[Клієнт C] Отримано звіт від сервера:\n%s", buf);
    }

    if (n < 0) {
        perror("read response");
        close(fd);
        return -1;
    }

    /* 4. Фінальне звільнення дескриптора сокета після отримання EOF */
    close(fd);
    return 0;
}

/* Функція сервера: прийом даних до EOF, формування звіту та закриття */
int run_half_close_server(int port) {
    int listen_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (listen_fd < 0) {
        perror("socket");
        return -1;
    }

    int opt = 1;
    setsockopt(listen_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons((uint16_t)port);

    if (bind(listen_fd, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        perror("bind");
        close(listen_fd);
        return -1;
    }

    if (listen(listen_fd, 16) < 0) {
        perror("listen");
        close(listen_fd);
        return -1;
    }

    int client_fd = accept(listen_fd, NULL, NULL);
    if (client_fd < 0) {
        perror("accept");
        close(listen_fd);
        return -1;
    }

    char buf[BUFFER_SIZE];
    size_t total_bytes = 0;
    size_t lines_count = 0;
    ssize_t n;

    /* Вичитка до отримання EOF (read повертає 0 при отриманні FIN) */
    while ((n = read(client_fd, buf, sizeof(buf))) > 0) {
        total_bytes += (size_t)n;
        for (ssize_t i = 0; i < n; ++i) {
            if (buf[i] == '\n') {
                lines_count++;
            }
        }
    }

    if (n < 0) {
        perror("read client data");
    } else {
        /* Формування та відправка підсумкового звіту клієнту */
        char report[256];
        int rlen = snprintf(report, sizeof(report),
                            "REPORT: OK. Прийнято %zu байтів, оброблено %zu рядків.\n",
                            total_bytes, lines_count);
        if (rlen > 0) {
            write(client_fd, report, (size_t)rlen);
        }
    }

    close(client_fd);
    close(listen_fd);
    return 0;
}
