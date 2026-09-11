#include <sys/socket.h>
#include <sys/time.h>
#include <chrono>
#include <system_error>

// Встановлення таймаутів у C++ за допомогою std::chrono
void configure_channel_timeouts(int sockfd, std::chrono::milliseconds timeout) {
    auto secs = std::chrono::duration_cast<std::chrono::seconds>(timeout);
    auto usecs = std::chrono::duration_cast<std::chrono::microseconds>(timeout - secs);

    struct timeval tv{};
    tv.tv_sec = secs.count();
    tv.tv_usec = usecs.count();

    if (::setsockopt(sockfd, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv)) < 0) {
        throw std::system_error(errno, std::generic_category(), "Failed to set SO_RCVTIMEO");
    }

    if (::setsockopt(sockfd, SOL_SOCKET, SO_SNDTIMEO, &tv, sizeof(tv)) < 0) {
        throw std::system_error(errno, std::generic_category(), "Failed to set SO_SNDTIMEO");
    }
}
