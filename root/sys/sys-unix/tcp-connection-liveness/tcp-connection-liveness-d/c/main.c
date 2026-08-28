#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/tcp.h>

int enable_keepalive(int fd) {
    int optval = 1;
    int idle = 30;   /* Почати зондування після 30с простою */
    int intvl = 5;   /* Повторювати зонди кожні 5с */
    int cnt = 3;     /* 3 невдалі спроби -> розрив */

    if (setsockopt(fd, SOL_SOCKET, SO_KEEPALIVE, &optval, sizeof(optval)) < 0)
        return -1;
    if (setsockopt(fd, IPPROTO_TCP, TCP_KEEPIDLE, &idle, sizeof(idle)) < 0)
        return -1;
    if (setsockopt(fd, IPPROTO_TCP, TCP_KEEPINTVL, &intvl, sizeof(intvl)) < 0)
        return -1;
    if (setsockopt(fd, IPPROTO_TCP, TCP_KEEPCNT, &cnt, sizeof(cnt)) < 0)
        return -1;

    return 0;
}
