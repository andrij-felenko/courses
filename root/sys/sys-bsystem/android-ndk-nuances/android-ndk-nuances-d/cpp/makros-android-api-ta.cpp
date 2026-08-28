#include <sys/epoll.h>
#include <sys/random.h>
#include <unistd.h>
#include <span>
#include <system_error>

namespace sys {
[[nodiscard]] inline int initialize_event_loop() {
    int fd = ::epoll_create1(EPOLL_CLOEXEC);
    if (fd < 0) {
        throw std::system_error(errno, std::generic_category(), "epoll_create1 failed");
    }
    return fd;
}

inline void fill_secure_random(std::span<std::byte> buffer) {
    ssize_t res = ::getrandom(buffer.data(), buffer.size_bytes(), 0);
    if (res < 0) {
        throw std::system_error(errno, std::generic_category(), "getrandom failed");
    }
}
} // namespace sys
