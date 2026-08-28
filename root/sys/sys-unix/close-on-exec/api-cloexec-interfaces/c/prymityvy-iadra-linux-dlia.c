#include <sys/epoll.h>
#include <sys/eventfd.h>
#include <unistd.h>

int init_event_subsystem(int *epoll_out, int *event_out) {
    int epfd = epoll_create1(EPOLL_CLOEXEC);
    if (epfd == -1)
        return -1;

    int evfd = eventfd(0, EFD_CLOEXEC | EFD_NONBLOCK);
    if (evfd == -1) {
        close(epfd);
        return -1;
    }

    *epoll_out = epfd;
    *event_out = evfd;
    return 0;
}
