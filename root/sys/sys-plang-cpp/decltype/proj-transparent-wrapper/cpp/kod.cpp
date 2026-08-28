#include <chrono>
#include <concepts>
#include <functional>
#include <utility>

// Зупиняє відлік у деструкторі — тому в тілі обгортки
// між викликом і `return` не буде жодної інструкції.
class tick_guard {
    std::chrono::steady_clock::time_point start_;
    std::chrono::nanoseconds& out_;
public:
    explicit tick_guard(std::chrono::nanoseconds& out) noexcept
        : start_(std::chrono::steady_clock::now()), out_(out) {}
    ~tick_guard() { out_ = std::chrono::steady_clock::now() - start_; }

    tick_guard(const tick_guard&) = delete;
    tick_guard& operator=(const tick_guard&) = delete;
};

template <class F, class... A>
    requires std::invocable<F, A...>
decltype(auto) timed(std::chrono::nanoseconds& out, F&& f, A&&... a)
    noexcept(noexcept(std::invoke(std::forward<F>(f), std::forward<A>(a)...)))
{
    tick_guard g{out};
    return std::invoke(std::forward<F>(f), std::forward<A>(a)...);
}
