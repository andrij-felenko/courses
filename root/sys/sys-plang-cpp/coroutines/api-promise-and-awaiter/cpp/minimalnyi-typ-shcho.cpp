#include <coroutine>
#include <exception>
#include <print>

struct fire_and_forget {
    struct promise_type {
        fire_and_forget get_return_object() noexcept { return {}; }
        std::suspend_never initial_suspend() noexcept { return {}; }
        std::suspend_never final_suspend() noexcept { return {}; }   // кадр гине сам
        void return_void() noexcept {}
        void unhandled_exception() { std::terminate(); }
    };
};

fire_and_forget log_later(int n) {
    co_await std::suspend_never{};   // await_ready() == true → призупинення не буде
    std::print("{}\n", n);           // n — копія, що лежить у кадрі
    co_return;                       // → return_void(), далі final_suspend і смерть кадру
}
