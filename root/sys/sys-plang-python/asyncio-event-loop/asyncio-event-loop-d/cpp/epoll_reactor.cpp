// epoll_reactor.cpp: Ідіоматична обгортка над системним селектором
#include <sys/epoll.h>
#include <unistd.h>
#include <span>
#include <system_error>

int wait_for_socket_event(int epoll_fd, int socket_fd, int timeout_ms) {
    epoll_event ev{};
    ev.events = EPOLLIN | EPOLLET;
    ev.data.fd = socket_fd;

    if (epoll_ctl(epoll_fd, EPOLL_CTL_ADD, socket_fd, &ev) < 0) {
        throw std::system_error(errno, std::generic_category(), "epoll_ctl error");
    }

    epoll_event active_events[1];
    int n = epoll_wait(epoll_fd, active_events, 1, timeout_ms);
    if (n < 0) {
        throw std::system_error(errno, std::generic_category(), "epoll_wait error");
    }
    return n;
}
