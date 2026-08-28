#include <iostream>
#include <vector>
#include <system_error>
#include <sys/epoll.h>
#include <unistd.h>

void monitor_cpp_pipe(int read_fd) {
    int ep_fd = ::epoll_create1(0);
    if (ep_fd == -1) {
        throw std::system_error(errno, std::generic_category(), "epoll_create1 failed");
    }

    epoll_event ev{};
    ev.events = EPOLLIN | EPOLLET;
    ev.data.fd = read_fd;

    if (::epoll_ctl(ep_fd, EPOLL_CTL_ADD, read_fd, &ev) == -1) {
        ::close(ep_fd);
        throw std::system_error(errno, std::generic_category(), "epoll_ctl failed");
    }

    std::vector<epoll_event> events(1);
    int nfds = ::epoll_wait(ep_fd, events.data(), 1, 5000);
    if (nfds > 0) {
        std::cout << "Data ready on read_fd: " << events[0].data.fd << "\n";
    }

    ::close(ep_fd);
}
