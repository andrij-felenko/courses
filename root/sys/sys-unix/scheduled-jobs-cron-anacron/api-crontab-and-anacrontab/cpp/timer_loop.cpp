#include "timer_loop.hpp"

#include <array>
#include <cerrno>
#include <cstring>
#include <format>
#include <iostream>
#include <stdexcept>

#include <sys/epoll.h>
#include <sys/prctl.h>
#include <sys/timerfd.h>
#include <unistd.h>

namespace minicron {
namespace {

constexpr int kEpollBatch = 8;

itimerspec to_itimerspec(std::chrono::nanoseconds first, std::chrono::nanoseconds interval)
{
    using namespace std::chrono;
    itimerspec spec{};
    spec.it_value.tv_sec = duration_cast<seconds>(first).count();
    spec.it_value.tv_nsec = (first % 1s).count();
    spec.it_interval.tv_sec = duration_cast<seconds>(interval).count();
    spec.it_interval.tv_nsec = (interval % 1s).count();
    return spec;
}

}  // namespace

TimerLoop::TimerLoop() : epoll_(::epoll_create1(EPOLL_CLOEXEC))
{
    if (!epoll_.valid()) {
        throw_errno("epoll_create1");
    }
}

void TimerLoop::register_source(std::unique_ptr<Source> source)
{
    epoll_event ev{};
    ev.events = EPOLLIN;
    ev.data.ptr = source.get();
    if (::epoll_ctl(epoll_.get(), EPOLL_CTL_ADD, source->fd, &ev) != 0) {
        throw_errno("epoll_ctl");
    }
    sources_.push_back(std::move(source));
}

void TimerLoop::add_timer(clockid_t clock, std::chrono::nanoseconds first,
                          std::chrono::nanoseconds interval, TimerCallback callback,
                          int flags)
{
    UniqueFd timer{::timerfd_create(clock, TFD_NONBLOCK | TFD_CLOEXEC)};
    if (!timer.valid()) {
        throw_errno("timerfd_create");
    }
    const itimerspec spec = to_itimerspec(first, interval);
    if (::timerfd_settime(timer.get(), flags, &spec, nullptr) != 0) {
        throw_errno("timerfd_settime");
    }

    auto source = std::make_unique<Source>();
    source->fd = timer.get();
    source->owned = std::move(timer);
    source->on_timer = std::move(callback);
    register_source(std::move(source));
}

void TimerLoop::watch(int fd, FdCallback callback)
{
    if (fd < 0) {
        throw std::invalid_argument("TimerLoop::watch: недійсний дескриптор");
    }
    auto source = std::make_unique<Source>();
    source->fd = fd;
    source->on_fd = std::move(callback);
    register_source(std::move(source));
}

void TimerLoop::run()
{
    std::array<epoll_event, kEpollBatch> events{};
    running_.store(true, std::memory_order_relaxed);

    while (running_.load(std::memory_order_relaxed)) {
        const int ready = ::epoll_wait(epoll_.get(), events.data(), kEpollBatch, -1);
        if (ready < 0) {
            if (errno == EINTR) {
                continue;   // сигнал: цикл сам перевірить прапорець
            }
            throw_errno("epoll_wait");
        }

        for (int i = 0; i < ready; ++i) {
            auto* source = static_cast<Source*>(events[i].data.ptr);
            if (source->on_fd) {
                source->on_fd(source->fd);
                continue;
            }

            std::uint64_t expirations = 0;
            const ssize_t n = ::read(source->fd, &expirations, sizeof expirations);
            if (n == static_cast<ssize_t>(sizeof expirations)) {
                // У лічильнику — скільки спрацьовувань накопичилося з минулого
                // читання; читання скидає його в нуль.
                source->on_timer(expirations);
            } else if (n < 0 && errno == ECANCELED) {
                // TFD_TIMER_CANCEL_ON_SET: годинник стрибнув. Будимо обробник
                // із нулем, щоб демон перерахував розклад.
                source->on_timer(0);
            } else if (n < 0 && errno != EAGAIN && errno != EWOULDBLOCK && errno != EINTR) {
                throw_errno("read timerfd");
            }
        }
    }
}

void TimerLoop::set_slack(std::chrono::nanoseconds slack)
{
    const auto value = static_cast<unsigned long>(slack.count());
    if (::prctl(PR_SET_TIMERSLACK, value, 0UL, 0UL, 0UL) != 0) {
        throw_errno("prctl(PR_SET_TIMERSLACK)");
    }
}

std::chrono::nanoseconds TimerLoop::read_slack()
{
    errno = 0;
    // PR_GET_TIMERSLACK віддає значення кодом повернення, тож -1 буває і
    // правильним числом — розрізняємо за errno.
    const int slack = ::prctl(PR_GET_TIMERSLACK, 0UL, 0UL, 0UL, 0UL);
    if (slack < 0 && errno != 0) {
        throw_errno("prctl(PR_GET_TIMERSLACK)");
    }
    return std::chrono::nanoseconds{slack};
}

}  // namespace minicron
