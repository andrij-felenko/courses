template<class Ref, class V, class Allocator>
class generator<Ref, V, Allocator>::promise_type {
public:
    // Створення генератора з обіцянки
    generator get_return_object() noexcept {
        return generator{std::coroutine_handle<promise_type>::from_promise(*this)};
    }

    // Початкове призупинення (лінивий запуск)
    std::suspend_always initial_suspend() noexcept { return {}; }

    // Фінальне призупинення повертає керування у батьківську корутину
    auto final_suspend() noexcept {
        struct final_awaiter {
            bool await_ready() noexcept { return false; }
            std::coroutine_handle<> await_suspend(std::coroutine_handle<promise_type> h) noexcept {
                if (h.promise().parent_) {
                    return h.promise().parent_; // Симетричне повернення в батьківський генератор
                }
                return std::noop_coroutine();
            }
            void await_resume() noexcept {}
        };
        return final_awaiter{};
    }

    // Збереження згенерованого значення
    std::suspend_always yield_value(yielded val) noexcept {
        value_ptr_ = std::addressof(val);
        return {};
    }

    void return_void() noexcept {}

    void unhandled_exception() {
        exception_ = std::current_exception();
    }

    // Підтримка користувацького розподілювача пам'яті
    template<class... Args>
    static void* operator new(std::size_t size, Args&&... args);
    static void operator delete(void* ptr, std::size_t size) noexcept;
private:
    std::addressof_t<yielded> value_ptr_{nullptr};
    std::exception_ptr exception_{nullptr};
    std::coroutine_handle<> parent_{nullptr};
};
