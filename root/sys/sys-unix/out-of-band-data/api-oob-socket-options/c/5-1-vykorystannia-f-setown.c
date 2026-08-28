#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>

int register_socket_owner(int sockfd) {
    if (fcntl(sockfd, F_SETOWN, getpid()) < 0) {
        perror("fcntl F_SETOWN");
        return -1;
    }
    return 0;
}
