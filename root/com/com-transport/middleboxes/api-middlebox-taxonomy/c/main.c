#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/tcp.h>

int configure_resilient_socket(int fd) {
    /* 1. Активація TCP Keepalive для утримання сесій у таблицях NAT */
    int keepalive = 1;
    if (setsockopt(fd, SOL_SOCKET, SO_KEEPALIVE, &keepalive, sizeof(keepalive)) < 0) {
        return -1;
    }

    /* Час бездіяльності до першого зонду (25 с для запобігання скидання CGNAT) */
    int keepidle = 25;
    if (setsockopt(fd, IPPROTO_TCP, TCP_KEEPIDLE, &keepidle, sizeof(keepidle)) < 0) {
        return -1;
    }

    /* Інтервал між повторними зондами */
    int keepintvl = 5;
    if (setsockopt(fd, IPPROTO_TCP, TCP_KEEPINTVL, &keepintvl, sizeof(keepintvl)) < 0) {
        return -1;
    }

    /* Кількість невдалих зондів до розриву сокета */
    int keepcnt = 3;
    if (setsockopt(fd, IPPROTO_TCP, TCP_KEEPCNT, &keepcnt, sizeof(keepcnt)) < 0) {
        return -1;
    }

    /* 2. Увімкнення TCP Fast Open на клієнті (RFC 7413) */
    int fastopen = 1;
    setsockopt(fd, IPPROTO_TCP, TCP_FASTOPEN_CONNECT, &fastopen, sizeof(fastopen));

    /* 3. Вимкнення алгоритму Нейгла для мінімізації затримок на проміжних проксі */
    int nodelay = 1;
    if (setsockopt(fd, IPPROTO_TCP, TCP_NODELAY, &nodelay, sizeof(nodelay)) < 0) {
        return -1;
    }

    return 0;
}
