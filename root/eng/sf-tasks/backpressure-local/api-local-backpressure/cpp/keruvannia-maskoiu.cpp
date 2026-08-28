#include <sys/epoll.h>
#include <cerrno>
#include <expected>
#include <system_error>

// Ідіоматичне керування маскою epoll для асинхронного протитиску
std::expected<void, std::error_code> toggle_source_reading(int epfd, int source_fd, bool enable_reading) {
    epoll_event ev{};
    ev.events = enable_reading ? (EPOLLIN | EPOLLRDHUP) : 0;
    ev.data.fd = source_fd;

    if (::epoll_ctl(epfd, EPOLL_CTL_MOD, source_fd, &ev) == -1) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return {};
}
