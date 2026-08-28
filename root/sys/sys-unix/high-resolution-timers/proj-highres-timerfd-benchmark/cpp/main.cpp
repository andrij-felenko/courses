#include <iostream>
#include <vector>
#include <chrono>
#include <numeric>
#include <algorithm>
#include <system_error>
#include <cstdint>
#include <cstdlib>
#include <cerrno>
#include <cmath>
#include <unistd.h>
#include <sys/timerfd.h>
#include <sys/epoll.h>

class TimerFd {
    int m_fd{-1};
public:
    explicit TimerFd(clockid_t clock_id) {
        m_fd = ::timerfd_create(clock_id, TFD_CLOEXEC);
        if (m_fd == -1) {
            throw std::system_error(errno, std::generic_category(), "timerfd_create failed");
        }
    }

    ~TimerFd() {
        if (m_fd != -1) {
            ::close(m_fd);
        }
    }

    TimerFd(const TimerFd&) = delete;
    TimerFd& operator=(const TimerFd&) = delete;

    TimerFd(TimerFd&& other) noexcept : m_fd(other.m_fd) {
        other.m_fd = -1;
    }

    int native_handle() const noexcept { return m_fd; }

    /* Абсолютна сітка: перший тик задано позначкою steady_clock (у Linux це
       CLOCK_MONOTONIC), тож ядро й програма рахують від одного нуля. */
    void arm(std::chrono::steady_clock::time_point first,
             std::chrono::nanoseconds period) {
        using std::chrono::duration_cast;
        using std::chrono::nanoseconds;
        using std::chrono::seconds;

        auto since = first.time_since_epoch();
        auto fsec = duration_cast<seconds>(since);
        auto psec = duration_cast<seconds>(period);

        struct itimerspec new_val{};
        new_val.it_value.tv_sec = fsec.count();
        new_val.it_value.tv_nsec = duration_cast<nanoseconds>(since - fsec).count();
        new_val.it_interval.tv_sec = psec.count();
        new_val.it_interval.tv_nsec = duration_cast<nanoseconds>(period - psec).count();

        if (::timerfd_settime(m_fd, TFD_TIMER_ABSTIME, &new_val, nullptr) == -1) {
            throw std::system_error(errno, std::generic_category(), "timerfd_settime failed");
        }
    }

    std::uint64_t wait_expirations() {
        std::uint64_t count{0};
        ssize_t res = ::read(m_fd, &count, sizeof(count));
        if (res != sizeof(count)) {
            throw std::system_error(errno, std::generic_category(), "timerfd read failed");
        }
        return count;
    }
};

int main() {
    constexpr std::size_t iterations = 10000;
    constexpr auto period = std::chrono::microseconds(500);

    try {
        TimerFd timer(CLOCK_MONOTONIC);
        
        int epfd = ::epoll_create1(EPOLL_CLOEXEC);
        if (epfd == -1) {
            throw std::system_error(errno, std::generic_category(), "epoll_create1 failed");
        }

        struct epoll_event ev{};
        ev.events = EPOLLIN;
        ev.data.fd = timer.native_handle();
        if (::epoll_ctl(epfd, EPOLL_CTL_ADD, timer.native_handle(), &ev) == -1) {
            ::close(epfd);
            throw std::system_error(errno, std::generic_category(), "epoll_ctl failed");
        }

        auto first_tick = std::chrono::steady_clock::now() + std::chrono::milliseconds(10);
        timer.arm(first_tick, period);

        auto expected_target = first_tick;
        std::vector<double> jitters_us;
        jitters_us.reserve(iterations);

        std::cout << "Розпочинаємо вимірювання C++ timerfd (10000 тиків)...\n";

        for (std::size_t i = 0; i < iterations; ++i) {
            struct epoll_event events[1];
            int nfds = ::epoll_wait(epfd, events, 1, -1);
            if (nfds < 0) {
                if (errno == EINTR) continue;
                throw std::system_error(errno, std::generic_category(), "epoll_wait failed");
            }

            std::uint64_t overruns = timer.wait_expirations();
            auto now = std::chrono::steady_clock::now();

            auto diff = std::chrono::duration_cast<std::chrono::nanoseconds>(now - expected_target);
            jitters_us.push_back(static_cast<double>(diff.count()) / 1000.0);

            expected_target += overruns * period;
        }

        ::close(epfd);

        auto [min_it, max_it] = std::minmax_element(jitters_us.begin(), jitters_us.end());
        double sum_abs = std::accumulate(jitters_us.begin(), jitters_us.end(), 0.0,
            [](double acc, double val) { return acc + std::abs(val); });

        std::cout << "\n=== Результати вимірювання джиттера C++ (10000 тиків) ===\n";
        std::cout << "Мінімальний джиттер : " << *min_it << " мкс\n";
        std::cout << "Максимальний джиттер: " << *max_it << " мкс\n";
        std::cout << "Середнє відхилення  : " << (sum_abs / iterations) << " мкс\n";

    } catch (const std::exception& ex) {
        std::cerr << "Помилка: " << ex.what() << '\n';
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
