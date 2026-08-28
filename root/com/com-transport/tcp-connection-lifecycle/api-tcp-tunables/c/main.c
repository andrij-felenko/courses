#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/tcp.h>

int configure_server_socket(int port) {
    int fd = socket(AF_INET, SOCK_STREAM, 0);
    if (fd < 0) {
        perror("socket");
        return -1;
    }

    /* 1. Дозволити миттєвий перезапуск сервера на порту у TIME_WAIT */
    int reuse_addr = 1;
    if (setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, &reuse_addr, sizeof(reuse_addr)) < 0) {
        perror("setsockopt SO_REUSEADDR");
        close(fd);
        return -1;
    }

    /* 2. Вимкнути затримку алгоритму Нейгла для швидкої реакції */
    int nodelay = 1;
    if (setsockopt(fd, IPPROTO_TCP, TCP_NODELAY, &nodelay, sizeof(nodelay)) < 0) {
        perror("setsockopt TCP_NODELAY");
        close(fd);
        return -1;
    }

    /* 3. Встановити користувацький таймаут доставки даних у 10 секунд */
    unsigned int user_timeout_ms = 10000;
    if (setsockopt(fd, IPPROTO_TCP, TCP_USER_TIMEOUT, &user_timeout_ms, sizeof(user_timeout_ms)) < 0) {
        perror("setsockopt TCP_USER_TIMEOUT");
        close(fd);
        return -1;
    }

    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_ANY);
    addr.sin_port = htons((uint16_t)port);

    if (bind(fd, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        perror("bind");
        close(fd);
        return -1;
    }

    if (listen(fd, 1024) < 0) {
        perror("listen");
        close(fd);
        return -1;
    }

    return fd;
}
