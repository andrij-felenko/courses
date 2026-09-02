// Мультиплексор подій: timerfd плюс сторонні дескриптори в одному epoll,
// без сигналів і без sleep().
#pragma once

#include "posix.hpp"

#include <atomic>
#include <chrono>
#include <cstdint>
#include <ctime>
#include <functional>
#include <memory>
#include <vector>

namespace minicron {

class TimerLoop {
public:
    using TimerCallback = std::function<void(std::uint64_t expirations)>;
    using FdCallback = std::function<void(int fd)>;

    TimerLoop();

    // flags — 0 (відносний час) або TFD_TIMER_ABSTIME, за потреби разом із
    // TFD_TIMER_CANCEL_ON_SET на CLOCK_REALTIME. Нульовий interval — разовий.
    void add_timer(clockid_t clock, std::chrono::nanoseconds first,
                   std::chrono::nanoseconds interval, TimerCallback callback,
                   int flags = 0);

    // Чужий дескриптор (inotify, сокет, канал): цикл лише будить обробник,
    // дані вичитує сам обробник. Дескриптор лишається у власності викликача.
    void watch(int fd, FdCallback callback);

    void run();
    void stop() noexcept { running_.store(false, std::memory_order_relaxed); }

    // Вікно коалесценції для ПОТОЧНОГО потоку (prctl(PR_SET_TIMERSLACK)):
    // ядро має право затримати спрацьовування настільки, щоб збігтися з уже
    // запланованим пробудженням процесора. Нуль повертає типове значення.
    static void set_slack(std::chrono::nanoseconds slack);
    static std::chrono::nanoseconds read_slack();

private:
    struct Source {
        UniqueFd owned;          // порожній для чужого дескриптора
        int fd = -1;
        TimerCallback on_timer;
        FdCallback on_fd;
    };

    void register_source(std::unique_ptr<Source> source);

    UniqueFd epoll_;
    // unique_ptr, бо адреса джерела їде в epoll_event::data.ptr і мусить
    // пережити будь-яке зростання вектора.
    std::vector<std::unique_ptr<Source>> sources_;
    std::atomic<bool> running_{false};
};

}  // namespace minicron
