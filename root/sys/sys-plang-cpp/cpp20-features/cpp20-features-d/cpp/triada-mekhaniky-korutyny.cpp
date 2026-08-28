#include <coroutine>
#include <iostream>

struct SimpleTask {
    struct promise_type {
        SimpleTask get_return_object() {
            return SimpleTask{std::coroutine_handle<promise_type>::from_promise(*this)};
        }
        std::suspend_never initial_suspend() noexcept { return {}; }
        std::suspend_always final_suspend() noexcept { return {}; }
        void return_void() noexcept {}
        void unhandled_exception() { std::terminate(); }
    };

    std::coroutine_handle<promise_type> handle;
    ~SimpleTask() { if (handle) handle.destroy(); }
};

SimpleTask async_counter() {
    std::cout << "Крок 1: початок обчислення\n";
    co_await std::suspend_always{}; // Точка призупинення
    std::cout << "Крок 2: продовження після відновлення\n";
}
