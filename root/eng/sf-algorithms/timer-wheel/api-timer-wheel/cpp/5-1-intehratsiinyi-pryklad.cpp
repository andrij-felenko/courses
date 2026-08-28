#include <sys/timerfd.h>
#include <sys/epoll.h>
#include <unistd.h>
#include <iostream>
#include <memory>
#include <array>

void setup_timer_event_loop_cpp(timer_wheel_t *tw, int epoll_fd) {
    int tfd = timerfd_create(CLOCK_MONOTONIC, TFD_NONBLOCK | TFD_CLOEXEC);
    
    struct itimerspec newValue{};
    newValue.it_interval.tv_nsec = 1000000; // 1 ms
    newValue.it_value.tv_nsec = 1000000;
    
    timerfd_settime(tfd, 0, &newValue, nullptr);
    
    struct epoll_event ev{};
    ev.events = EPOLLIN | EPOLLET;
    ev.data.fd = tfd;
    epoll_ctl(epoll_fd, EPOLL_CTL_ADD, tfd, &ev);
    
    std::array<struct epoll_event, 16> events{};
    while (true) {
        int nfds = epoll_wait(epoll_fd, events.data(), static_cast<int>(events.size()), -1);
        for (int i = 0; i < nfds; ++i) {
            if (events[i].data.fd == tfd) {
                uint64_t expirations = 0;
                ssize_t s = read(tfd, &expirations, sizeof(expirations));
                if (s > 0) {
                    for (uint64_t e = 0; e < expirations; ++e) {
                        uint32_t executed = 0;
                        timer_wheel_tick(tw, &executed);
                    }
                }
            }
        }
    }
}
