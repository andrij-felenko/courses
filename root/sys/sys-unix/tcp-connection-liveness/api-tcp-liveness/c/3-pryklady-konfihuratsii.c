#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/tcp.h>

int configure_tcp_liveness(int fd, int idle_sec, int intvl_sec, int cnt, unsigned int user_timeout_ms) {
    int enable = 1;
    if (setsockopt(fd, SOL_SOCKET, SO_KEEPALIVE, &enable, sizeof(enable)) < 0) {
        perror("setsockopt(SO_KEEPALIVE)");
        return -1;
    }

    if (setsockopt(fd, IPPROTO_TCP, TCP_KEEPIDLE, &idle_sec, sizeof(idle_sec)) < 0) {
        perror("setsockopt(TCP_KEEPIDLE)");
        return -1;
    }

    if (setsockopt(fd, IPPROTO_TCP, TCP_KEEPINTVL, &intvl_sec, sizeof(intvl_sec)) < 0) {
        perror("setsockopt(TCP_KEEPINTVL)");
        return -1;
    }

    if (setsockopt(fd, IPPROTO_TCP, TCP_KEEPCNT, &cnt, sizeof(cnt)) < 0) {
        perror("setsockopt(TCP_KEEPCNT)");
        return -1;
    }

    if (user_timeout_ms > 0) {
        if (setsockopt(fd, IPPROTO_TCP, TCP_USER_TIMEOUT, &user_timeout_ms, sizeof(user_timeout_ms)) < 0) {
            perror("setsockopt(TCP_USER_TIMEOUT)");
            return -1;
        }
    }

    return 0;
}
