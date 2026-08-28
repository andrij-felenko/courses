#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/tcp.h>

void configure_streaming_socket(int sock_fd) noexcept {
    constexpr int kBufferSize = 128 * 1024;
    ::setsockopt(sock_fd, SOL_SOCKET, SO_RCVBUF, &kBufferSize, sizeof(kBufferSize));
    ::setsockopt(sock_fd, SOL_SOCKET, SO_SNDBUF, &kBufferSize, sizeof(kBufferSize));

    constexpr int kNoDelay = 1;
    ::setsockopt(sock_fd, IPPROTO_TCP, TCP_NODELAY, &kNoDelay, sizeof(kNoDelay));
}
