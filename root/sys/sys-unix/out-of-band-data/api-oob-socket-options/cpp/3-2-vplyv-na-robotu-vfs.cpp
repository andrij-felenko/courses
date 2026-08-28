#include <sys/socket.h>
#include <system_error>
#include <iostream>

void set_oob_inline(int sockfd, bool enable) {
    int optval = enable ? 1 : 0;
    if (::setsockopt(sockfd, SOL_SOCKET, SO_OOBINLINE, &optval, sizeof(optval)) < 0) {
        throw std::system_error(errno, std::generic_category(), "setsockopt SO_OOBINLINE failed");
    }
}
