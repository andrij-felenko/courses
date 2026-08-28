#include <sys/socket.h>
#include <netinet/tcp.h>
#include <optional>

std::optional<::tcp_info> fetch_tcp_info(int sockfd) {
    ::tcp_info info{};
    ::socklen_t len = sizeof(info);
    if (::getsockopt(sockfd, IPPROTO_TCP, TCP_INFO, &info, &len) == 0) {
        return info;
    }
    return std::nullopt;
}
