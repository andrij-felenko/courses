#include <sys/epoll.h>
#include <stdbool.h>
#include <errno.h>

/* Призупинення або відновлення читання з дескриптора джерела */
int toggle_source_reading(int epfd, int source_fd, bool enable_reading) {
    struct epoll_event ev;
    ev.events = enable_reading ? (EPOLLIN | EPOLLRDHUP) : 0;
    ev.data.fd = source_fd;

    if (epoll_ctl(epfd, EPOLL_CTL_MOD, source_fd, &ev) == -1) {
        return -errno;
    }
    return 0;
}
