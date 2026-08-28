#include <string_view>
#include <system_error>
#include <sys/socket.h>
#include <netinet/tcp.h>

void set_congestion(int sockfd, std::string_view algo) {
    if (::setsockopt(sockfd, IPPROTO_TCP, TCP_CONGESTION, algo.data(), algo.size() + 1) < 0) {
        throw std::system_error(errno, std::generic_category(), "setsockopt TCP_CONGESTION failed");
    }
}
