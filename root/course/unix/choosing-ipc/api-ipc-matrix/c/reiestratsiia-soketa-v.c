#include <sys/epoll.h>
#include <string.h>

int register_socket_in_epoll(int epoll_fd, int sock_fd) {
    struct epoll_event ev;
    memset(&ev, 0, sizeof(ev));
    ev.events = EPOLLIN | EPOLLRDHUP | EPOLLET; /* Готовність читання + контроль закриття */
    ev.data.fd = sock_fd;
    return epoll_ctl(epoll_fd, EPOLL_CTL_ADD, sock_fd, &ev);
}
