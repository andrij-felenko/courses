#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/tcp.h>

int configure_tcp_keepalive(int fd, int idle_sec, int interval_sec, int count, unsigned int user_timeout_ms) {
    int enable = 1;
    if (setsockopt(fd, SOL_SOCKET, SO_KEEPALIVE, &enable, sizeof(enable)) < 0) {
        perror("setsockopt(SO_KEEPALIVE)");
        return -1;
    }

#ifdef __linux__
    if (setsockopt(fd, IPPROTO_TCP, TCP_KEEPIDLE, &idle_sec, sizeof(idle_sec)) < 0) {
        perror("setsockopt(TCP_KEEPIDLE)");
        return -1;
    }
#elif defined(__APPLE__) || defined(__FreeBSD__) || defined(__NetBSD__) || defined(__OpenBSD__)
    if (setsockopt(fd, IPPROTO_TCP, TCP_KEEPALIVE, &idle_sec, sizeof(idle_sec)) < 0) {
        perror("setsockopt(TCP_KEEPALIVE)");
        return -1;
    }
#endif

    if (setsockopt(fd, IPPROTO_TCP, TCP_KEEPINTVL, &interval_sec, sizeof(interval_sec)) < 0) {
        perror("setsockopt(TCP_KEEPINTVL)");
        return -1;
    }

    if (setsockopt(fd, IPPROTO_TCP, TCP_KEEPCNT, &count, sizeof(count)) < 0) {
        perror("setsockopt(TCP_KEEPCNT)");
        return -1;
    }

#ifdef TCP_USER_TIMEOUT
    if (user_timeout_ms > 0) {
        if (setsockopt(fd, IPPROTO_TCP, TCP_USER_TIMEOUT, &user_timeout_ms, sizeof(user_timeout_ms)) < 0) {
            perror("setsockopt(TCP_USER_TIMEOUT)");
            return -1;
        }
    }
#endif

    return 0;
}
