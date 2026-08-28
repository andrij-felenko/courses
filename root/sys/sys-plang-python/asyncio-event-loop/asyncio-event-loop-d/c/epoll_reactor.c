// epoll_reactor.c: Низькорівневе очікування подій сокета
#include <sys/epoll.h>
#include <unistd.h>

int wait_for_socket_event(int epoll_fd, int socket_fd, int timeout_ms) {
    struct epoll_event event;
    event.events = EPOLLIN | EPOLLET; // Edge-Triggered читання
    event.data.fd = socket_fd;
    
    if (epoll_ctl(epoll_fd, EPOLL_CTL_ADD, socket_fd, &event) < 0) {
        return -1;
    }
    
    struct epoll_event active_events[1];
    int n = epoll_wait(epoll_fd, active_events, 1, timeout_ms);
    return n; // Кількість активних подій
}
