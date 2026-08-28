#include <sys/epoll.h>
#include <system_error>
#include <cerrno>

void register_socket_in_epoll(int epoll_fd, int sock_fd) {
    struct epoll_event ev{};
    ev.events = EPOLLIN | EPOLLRDHUP | EPOLLET;
    ev.data.fd = sock_fd;
    if (::epoll_ctl(epoll_fd, EPOLL_CTL_ADD, sock_fd, &ev) < 0) {
        throw std::system_error(errno, std::generic_category(), "epoll_ctl failed");
    }
}
