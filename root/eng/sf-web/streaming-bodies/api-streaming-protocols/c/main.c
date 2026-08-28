#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/tcp.h>

void configure_streaming_socket(int sock_fd) {
    int rcvbuf = 128 * 1024;
    setsockopt(sock_fd, SOL_SOCKET, SO_RCVBUF, &rcvbuf, sizeof(rcvbuf));

    int sndbuf = 128 * 1024;
    setsockopt(sock_fd, SOL_SOCKET, SO_SNDBUF, &sndbuf, sizeof(sndbuf));

    int nodelay = 1;
    setsockopt(sock_fd, IPPROTO_TCP, TCP_NODELAY, &nodelay, sizeof(nodelay));
}
