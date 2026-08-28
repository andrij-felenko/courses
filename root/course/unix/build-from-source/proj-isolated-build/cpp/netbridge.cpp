// netbridge.cpp — Ідіоматична C++ реалізація з RAII-обгорткою над uv_loop
#include <iostream>
#include <memory>
#include <expected>
#include <system_error>
#include <uv.h>

class UvLoopRunner {
    uv_loop_t* loop_{nullptr};
public:
    UvLoopRunner() : loop_(uv_default_loop()) {}
    ~UvLoopRunner() noexcept {
        if (loop_) {
            uv_loop_close(loop_);
        }
    }
    UvLoopRunner(const UvLoopRunner&) = delete;
    UvLoopRunner& operator=(const UvLoopRunner&) = delete;
    UvLoopRunner(UvLoopRunner&& other) noexcept : loop_(other.loop_) {
        other.loop_ = nullptr;
    }
    UvLoopRunner& operator=(UvLoopRunner&& other) noexcept {
        if (this != &other) {
            if (loop_) uv_loop_close(loop_);
            loop_ = other.loop_;
            other.loop_ = nullptr;
        }
        return *this;
    }

    [[nodiscard]] uv_loop_t* get() const noexcept { return loop_; }
    void run() const noexcept {
        if (loop_) {
            uv_run(loop_, UV_RUN_DEFAULT);
        }
    }
};

static void timer_callback(uv_timer_t* handle) {
    auto uptime = uv_now(handle->loop);
    std::cout << "[netbridge-cpp] Сервіс працює. Час: " << uptime << " мс\n";
    uv_timer_stop(handle);
    uv_stop(handle->loop);
}

int main() {
    std::cout << "[netbridge-cpp] Ініціалізація C++ сервісу...\n";
    UvLoopRunner runner;
    if (!runner.get()) {
        std::cerr << "Не вдалося отримати системний loop\n";
        return 1;
    }

    uv_timer_t timer;
    if (int err = uv_timer_init(runner.get(), &timer); err < 0) {
        std::cerr << "Помилка таймера: " << uv_strerror(err) << "\n";
        return 1;
    }

    uv_timer_start(&timer, timer_callback, 100, 0);
    runner.run();
    std::cout << "[netbridge-cpp] Завершення.\n";
    return 0;
}
