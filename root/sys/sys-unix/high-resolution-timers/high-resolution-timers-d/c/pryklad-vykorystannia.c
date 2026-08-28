#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <unistd.h>
#include <sys/timerfd.h>
#include <sys/epoll.h>
#include <time.h>

int main(void) {
    int tfd = timerfd_create(CLOCK_MONOTONIC, TFD_NONBLOCK | TFD_CLOEXEC);
    if (tfd == -1) {
        perror("timerfd_create");
        return EXIT_FAILURE;
    }

    struct itimerspec new_value = {0};
    /* Період 1 мілісекунда = 1 000 000 наносекунд */
    new_value.it_interval.tv_sec = 0;
    new_value.it_interval.tv_nsec = 1000000;
    new_value.it_value.tv_sec = 0;
    new_value.it_value.tv_nsec = 1000000;

    if (timerfd_settime(tfd, 0, &new_value, NULL) == -1) {
        perror("timerfd_settime");
        close(tfd);
        return EXIT_FAILURE;
    }

    int epfd = epoll_create1(EPOLL_CLOEXEC);
    if (epfd == -1) {
        perror("epoll_create1");
        close(tfd);
        return EXIT_FAILURE;
    }

    struct epoll_event ev;
    ev.events = EPOLLIN;
    ev.data.fd = tfd;
    if (epoll_ctl(epfd, EPOLL_CTL_ADD, tfd, &ev) == -1) {
        perror("epoll_ctl");
        close(epfd);
        close(tfd);
        return EXIT_FAILURE;
    }

    printf("Чекаємо 5 спрацьовувань timerfd...\n");
    for (int i = 0; i < 5; i++) {
        struct epoll_event events[1];
        int nfds = epoll_wait(epfd, events, 1, -1);
        if (nfds > 0) {
            uint64_t overruns = 0;
            ssize_t s = read(tfd, &overruns, sizeof(overruns));
            if (s == sizeof(overruns)) {
                printf("Тик %d: спрацьовувань за інтервал = %llu\n", i + 1, (unsigned long long)overruns);
            }
        }
    }

    close(epfd);
    close(tfd);
    return EXIT_SUCCESS;
}
