#include <sys/epoll.h>
#include <sys/eventfd.h>
#include <unistd.h>
#include <system_error>
#include <utility>

std::pair<int, int> init_event_subsystem() {
    int epfd = ::epoll_create1(EPOLL_CLOEXEC);
    if (epfd == -1) {
        throw std::system_error(errno, std::generic_category(), "epoll_create1 failed");
    }

    int evfd = ::eventfd(0, EFD_CLOEXEC | EFD_NONBLOCK);
    if (evfd == -1) {
        ::close(epfd);
        throw std::system_error(errno, std::generic_category(), "eventfd failed");
    }

    return {epfd, evfd};
}
