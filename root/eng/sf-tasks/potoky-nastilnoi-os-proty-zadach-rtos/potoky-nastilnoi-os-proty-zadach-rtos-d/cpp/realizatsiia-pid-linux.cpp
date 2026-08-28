#include <iostream>
#include <chrono>
#include <thread>
#include <mutex>
#include <expected>
#include <system_error>
#include <pthread.h>
#include <sched.h>
#include <sys/mman.h>

class RealTimeThreadController {
public:
    using Clock = std::chrono::steady_clock;

    RealTimeThreadController() {
        // Блокування сторінок пам'яті для усунення Page Faults
        if (mlockall(MCL_CURRENT | MCL_FUTURE) != 0) {
            throw std::system_error(errno, std::generic_category(), "mlockall failed");
        }

        // Ініціалізація нативного м'ютекса з PTHREAD_PRIO_INHERIT
        pthread_mutexattr_t mattr;
        pthread_mutexattr_init(&mattr);
        pthread_mutexattr_setprotocol(&mattr, PTHREAD_PRIO_INHERIT);
        pthread_mutex_init(&native_mutex_, &mattr);
        pthread_mutexattr_destroy(&mattr);
    }

    ~RealTimeThreadController() {
        stop_requested_ = true;
        if (worker_.joinable()) {
            worker_.join();
        }
        pthread_mutex_destroy(&native_mutex_);
    }

    void start() {
        worker_ = std::jthread([this](std::stop_token stoken) {
            configure_realtime_priority();
            run_loop(stoken);
        });
    }

private:
    void configure_realtime_priority() {
        sched_param param{.sched_priority = 99};
        if (pthread_setschedparam(pthread_self(), SCHED_FIFO, &param) != 0) {
            std::cerr << "Помилка встановлення SCHED_FIFO: потрібні привілеї root\n";
        }
    }

    void run_loop(std::stop_token stoken) {
        using namespace std::chrono_literals;
        constexpr auto period = 1ms;
        auto next_tick = Clock::now();

        while (!stoken.stop_requested() && !stop_requested_) {
            next_tick += period;
            std::this_thread::sleep_until(next_tick);

            // Використання нативного м'ютекса з RAII-блокуванням
            if (pthread_mutex_lock(&native_mutex_) == 0) {
                perform_control_update();
                pthread_mutex_unlock(&native_mutex_);
            }
        }
    }

    void perform_control_update() noexcept {
        // Обчислювальний крок без виділення динамічної пам'яті
    }

    pthread_mutex_t native_mutex_;
    std::jthread worker_;
    bool stop_requested_{false};
};
