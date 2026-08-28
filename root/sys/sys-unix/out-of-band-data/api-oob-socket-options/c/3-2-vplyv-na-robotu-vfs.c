#include <sys/socket.h>
#include <stdio.h>
#include <errno.h>

int set_oob_inline(int sockfd, int enable) {
    int optval = enable ? 1 : 0;
    if (setsockopt(sockfd, SOL_SOCKET, SO_OOBINLINE, &optval, sizeof(optval)) < 0) {
        perror("setsockopt SO_OOBINLINE");
        return -1;
    }
    return 0;
}
