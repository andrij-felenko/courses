#include <chrono>
#include <coroutine>
#include <stop_token>

// Очікуваний об'єкт таймера з підтримкою скасування через stop_token
struct cancellable_sleep {
    std::chrono::milliseconds duration;
    std::stop_token stoken;

    bool await_ready() const noexcept {
        // Якщо зупинка вже надійшла — не призупиняємося взагалі
        return stoken.stop_requested() || duration.count() <= 0;
    }

    void await_suspend(std::coroutine_handle<> handle) {
        // Реєструємо зворотний виклик для миттєвого відновлення корутини при скасуванні
        cb_.emplace(stoken, [handle] {
            handle.resume();
        });

        // Запускаємо асинхронний таймер (у спрощеному вигляді — окремий тайм-потік або таймер epoll/kqueue)
        timer_thread_ = std::jthread([this, handle] {
            std::this_thread::sleep_for(duration);
            if (cb_.has_value()) {
                handle.resume();
            }
        });
    }

    bool await_resume() const noexcept {
        // Повертає true, якщо таймер сплив успішно, або false, якщо його було скасовано
        return !stoken.stop_requested();
    }

private:
    std::optional<std::stop_callback<std::function<void()>>> cb_;
    std::jthread timer_thread_;
};
