#include <iostream>
#include <vector>
#include <queue>
#include <chrono>
#include <functional>
#include <memory>
#include <system_error>
#include <unistd.h>
#include <fcntl.h>
#include <sys/epoll.h>

class EventLoop {
public:
    using EventCallback = std::function<void(uint32_t events)>;
    using TimerCallback = std::function<void()>;

    EventLoop() {
        epoll_fd_ = epoll_create1(EPOLL_CLOEXEC);
        if (epoll_fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "epoll_create1 failed");
        }
    }

    ~EventLoop() {
        if (epoll_fd_ >= 0) {
            ::close(epoll_fd_);
        }
    }

    void add_fd(int fd, uint32_t events, EventCallback cb) {
        auto cb_ptr = std::make_unique<EventCallback>(std::move(cb));
        epoll_event ev{};
        ev.events = events;
        ev.data.ptr = cb_ptr.get();

        if (epoll_ctl(epoll_fd_, EPOLL_CTL_ADD, fd, &ev) < 0) {
            throw std::system_error(errno, std::generic_category(), "epoll_ctl ADD failed");
        }
        fd_callbacks_.push_back(std::move(cb_ptr));
    }

    void add_timer(std::chrono::milliseconds delay, TimerCallback cb) {
        auto deadline = std::chrono::steady_clock::now() + delay;
        timers_.push(TimerEntry{deadline, ++next_id_, std::move(cb)});
    }

    void stop() noexcept {
        running_ = false;
    }

    void run() {
        running_ = true;
        constexpr int max_events = 64;
        epoll_event events[max_events];

        while (running_) {
            auto now = std::chrono::steady_clock::now();

            // 1. Розрахунок таймауту для ядра
            int timeout_ms = -1;
            if (!timers_.empty()) {
                if (timers_.top().deadline <= now) {
                    timeout_ms = 0;
                } else {
                    auto diff = std::chrono::duration_cast<std::chrono::milliseconds>(
                        timers_.top().deadline - now
                    ).count();
                    timeout_ms = static_cast<int>(diff);
                }
            }

            // 2. Очікування подій від ядра
            int nfds = epoll_wait(epoll_fd_, events, max_events, timeout_ms);
            if (nfds < 0 && errno != EINTR) {
                throw std::system_error(errno, std::generic_category(), "epoll_wait failed");
            }

            // 3. Виклик обробників I/O
            for (int i = 0; i < nfds; ++i) {
                auto* cb = static_cast<EventCallback*>(events[i].data.ptr);
                if (cb && *cb) {
                    (*cb)(events[i].events);
                }
            }

            // 4. Виклик прострочених таймерів
            now = std::chrono::steady_clock::now();
            while (!timers_.empty() && timers_.top().deadline <= now) {
                auto entry = std::move(const_cast<TimerEntry&>(timers_.top()));
                timers_.pop();
                if (entry.callback) {
                    entry.callback();
                }
            }
        }
    }

private:
    struct TimerEntry {
        std::chrono::steady_clock::time_point deadline;
        uint64_t id;
        TimerCallback callback;

        bool operator>(const TimerEntry& other) const noexcept {
            return deadline > other.deadline;
        }
    };

    int epoll_fd_{-1};
    bool running_{false};
    uint64_t next_id_{0};
    std::priority_queue<TimerEntry, std::vector<TimerEntry>, std::greater<TimerEntry>> timers_;
    std::vector<std::unique_ptr<EventCallback>> fd_callbacks_;
};
