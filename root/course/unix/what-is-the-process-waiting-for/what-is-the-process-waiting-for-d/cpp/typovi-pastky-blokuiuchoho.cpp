#include <sys/socket.h>
#include <sys/time.h>
#include <chrono>
#include <system_error>
#include <unistd.h>

void configure_socket_timeouts(int sockfd, std::chrono::seconds timeout) {
    struct timeval tv{};
    tv.tv_sec = timeout.count();
    tv.tv_usec = 0;

    if (setsockopt(sockfd, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv)) < 0) {
        throw std::system_error(errno, std::generic_category(), "Помилка встановлення SO_RCVTIMEO");
    }

    if (setsockopt(sockfd, SOL_SOCKET, SO_SNDTIMEO, &tv, sizeof(tv)) < 0) {
        throw std::system_error(errno, std::generic_category(), "Помилка встановлення SO_SNDTIMEO");
    }
}
