#include <future>
#include <coroutine>

template <typename T>
struct future_awaiter {
    std::future<T> fut;

    bool await_ready() const noexcept {
        return fut.wait_for(std::chrono::seconds(0)) == std::future_status::ready;
    }

    void await_suspend(std::coroutine_handle<> h) {
        std::thread([this, h]() mutable {
            fut.wait();
            h.resume(); // Відновлюємо корутину у фоновому потоці
        }).detach();
    }

    T await_resume() {
        return fut.get();
    }
};

template <typename T>
auto operator co_await(std::future<T> fut) {
    return future_awaiter<T>{std::move(fut)};
}
