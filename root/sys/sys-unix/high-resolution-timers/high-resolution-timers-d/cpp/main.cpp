#include <iostream>
#include <chrono>
#include <system_error>
#include <cstdint>
#include <cstdlib>
#include <cerrno>
#include <unistd.h>
#include <sys/timerfd.h>
#include <sys/epoll.h>

class HighResTimer {
    int m_tfd{-1};
public:
    explicit HighResTimer(std::chrono::nanoseconds period) {
        m_tfd = ::timerfd_create(CLOCK_MONOTONIC, TFD_NONBLOCK | TFD_CLOEXEC);
        if (m_tfd == -1) {
            throw std::system_error(errno, std::generic_category(), "timerfd_create failed");
        }

        struct itimerspec new_val{};
        auto secs = std::chrono::duration_cast<std::chrono::seconds>(period);
        auto nsecs = period - secs;

        new_val.it_interval.tv_sec = secs.count();
        new_val.it_interval.tv_nsec = nsecs.count();
        new_val.it_value = new_val.it_interval;

        if (::timerfd_settime(m_tfd, 0, &new_val, nullptr) == -1) {
            ::close(m_tfd);
            throw std::system_error(errno, std::generic_category(), "timerfd_settime failed");
        }
    }

    ~HighResTimer() {
        if (m_tfd != -1) {
            ::close(m_tfd);
        }
    }

    int fd() const noexcept { return m_tfd; }

    std::uint64_t read_overruns() {
        std::uint64_t overruns{0};
        ssize_t s = ::read(m_tfd, &overruns, sizeof(overruns));
        if (s != sizeof(overruns)) {
            throw std::system_error(errno, std::generic_category(), "read failed");
        }
        return overruns;
    }
};

int main() {
    try {
        using namespace std::chrono_literals;
        HighResTimer timer(1ms);

        int epfd = ::epoll_create1(EPOLL_CLOEXEC);
        if (epfd == -1) {
            throw std::system_error(errno, std::generic_category(), "epoll_create1 failed");
        }

        struct epoll_event ev{};
        ev.events = EPOLLIN;
        ev.data.fd = timer.fd();
        ::epoll_ctl(epfd, EPOLL_CTL_ADD, timer.fd(), &ev);

        std::cout << "Чекаємо 5 спрацьовувань C++ timerfd...\n";
        for (int i = 0; i < 5; ++i) {
            struct epoll_event events[1];
            int nfds = ::epoll_wait(epfd, events, 1, -1);
            if (nfds > 0) {
                auto count = timer.read_overruns();
                std::cout << "C++ Тик " << (i + 1) << ": спрацьовувань = " << count << '\n';
            }
        }

        ::close(epfd);
    } catch (const std::exception& ex) {
        std::cerr << "Помилка: " << ex.what() << '\n';
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
