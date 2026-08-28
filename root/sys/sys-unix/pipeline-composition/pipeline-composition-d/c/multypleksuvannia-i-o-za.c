#include <sys/epoll.h>
#include <stdio.h>
#include <unistd.h>

void monitor_pipe_events(int read_fd) {
    int epoll_fd = epoll_create1(0);
    struct epoll_event ev, events[1];

    ev.events = EPOLLIN | EPOLLET; // Читання + Edge-Triggered режим
    ev.data.fd = read_fd;
    epoll_ctl(epoll_fd, EPOLL_CTL_ADD, read_fd, &ev);

    printf("Waiting for data on pipe...\n");
    int nfds = epoll_wait(epoll_fd, events, 1, 5000); // 5 секунд таймаут
    if (nfds > 0) {
        printf("Data is ready to be read from pipe!\n");
    } else {
        printf("Timeout or no data.\n");
    }

    close(epoll_fd);
}
