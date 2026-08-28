class Epoll {
    int epfd_;
public:
    Epoll() : epfd_(epoll_create1(EPOLL_CLOEXEC)) {
        if (epfd_ < 0) throw std::system_error(errno, std::generic_category(), "epoll_create1");
    }
    ~Epoll() { if (epfd_ >= 0) ::close(epfd_); }

    void add(int fd, uint32_t events) {
        struct epoll_event ev{};
        ev.events = events;
        ev.data.fd = fd;
        if (epoll_ctl(epfd_, EPOLL_CTL_ADD, fd, &ev) < 0) {
            throw std::system_error(errno, std::generic_category(), "epoll_ctl");
        }
    }

    int wait(std::span<struct epoll_event> events, int timeout_ms) {
        int n = epoll_wait(epfd_, events.data(), static_cast<int>(events.size()), timeout_ms);
        if (n < 0 && errno != EINTR) {
            throw std::system_error(errno, std::generic_category(), "epoll_wait");
        }
        return n;
    }
};

Epoll ep;
ep.add(conn_fd, EPOLLIN);

std::array<struct epoll_event, 64> events;
for (;;) {
    int n = ep.wait(events, -1);
    for (int i = 0; i < n; i++) {
        handle_data(events[i].data.fd);
    }
}
