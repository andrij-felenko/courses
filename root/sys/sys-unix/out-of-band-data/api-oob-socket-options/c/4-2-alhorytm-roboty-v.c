#include <sys/ioctl.h>
#include <stdio.h>

int is_socket_at_mark(int sockfd) {
    int mark = 0;
    if (ioctl(sockfd, SIOCATMARK, &mark) < 0) {
        perror("ioctl SIOCATMARK");
        return -1;
    }
    return mark; // 1 — на маркері, 0 — ні
}
