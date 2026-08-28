#include <system_error>
#include <chrono>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/tcp.h>

void setup_tcp_keepalive(int fd, std::chrono::seconds idle, std::chrono::seconds intvl, int cnt) {
    int optval = 1;
    if (::setsockopt(fd, SOL_SOCKET, SO_KEEPALIVE, &optval, sizeof(optval)) < 0) {
        throw std::system_error(errno, std::generic_category(), "Failed to enable SO_KEEPALIVE");
    }

    int idle_sec = static_cast<int>(idle.count());
    if (::setsockopt(fd, IPPROTO_TCP, TCP_KEEPIDLE, &idle_sec, sizeof(idle_sec)) < 0) {
        throw std::system_error(errno, std::generic_category(), "Failed to set TCP_KEEPIDLE");
    }

    int intvl_sec = static_cast<int>(intvl.count());
    if (::setsockopt(fd, IPPROTO_TCP, TCP_KEEPINTVL, &intvl_sec, sizeof(intvl_sec)) < 0) {
        throw std::system_error(errno, std::generic_category(), "Failed to set TCP_KEEPINTVL");
    }

    if (::setsockopt(fd, IPPROTO_TCP, TCP_KEEPCNT, &cnt, sizeof(cnt)) < 0) {
        throw std::system_error(errno, std::generic_category(), "Failed to set TCP_KEEPCNT");
    }
}
