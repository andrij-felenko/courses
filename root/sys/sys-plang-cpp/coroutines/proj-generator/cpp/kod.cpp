#include <coroutine>
#include <exception>
#include <iterator>
#include <memory>
#include <utility>

template <class T>
class generator {
public:
    struct promise_type {
        const T*           value = nullptr;   // дивиться всередину виразу co_yield
        std::exception_ptr error;

        generator get_return_object() noexcept {
            return generator{
                std::coroutine_handle<promise_type>::from_promise(*this) };
        }

        std::suspend_always initial_suspend() const noexcept { return {}; }  // лінивий старт
        std::suspend_always final_suspend()   const noexcept { return {}; }  // кадр не гине сам

        std::suspend_always yield_value(const T& v) noexcept {
            value = std::addressof(v);
            return {};
        }

        void return_void() const noexcept {}
        void unhandled_exception() noexcept { error = std::current_exception(); }

        void await_transform() = delete;      // co_await у цьому типі заборонено

        void rethrow_if_error() const {
            if (error) std::rethrow_exception(error);
        }
    };

    generator(generator&& other) noexcept : h_{ std::exchange(other.h_, {}) } {}

    generator& operator=(generator&& other) noexcept {
        if (this != &other) {
            if (h_) h_.destroy();
            h_ = std::exchange(other.h_, {});
        }
        return *this;
    }

    generator(const generator&)            = delete;
    generator& operator=(const generator&) = delete;

    ~generator() { if (h_) h_.destroy(); }

    struct sentinel {};

    class iterator {
    public:
        using iterator_concept = std::input_iterator_tag;
        using value_type       = T;
        using difference_type  = std::ptrdiff_t;

        iterator() = default;
        explicit iterator(std::coroutine_handle<promise_type> h) noexcept : h_{ h } {}

        const T& operator*()  const noexcept { return *h_.promise().value; }
        const T* operator->() const noexcept { return  h_.promise().value; }

        iterator& operator++() {
            h_.resume();
            h_.promise().rethrow_if_error();
            return *this;
        }
        void operator++(int) { ++*this; }

        bool operator==(sentinel) const noexcept { return !h_ || h_.done(); }

    private:
        std::coroutine_handle<promise_type> h_{};
    };

    iterator begin() {
        if (h_ && !h_.done()) {
            h_.resume();                      // доводимо тіло до першого co_yield
            h_.promise().rethrow_if_error();
        }
        return iterator{ h_ };
    }

    sentinel end() const noexcept { return {}; }

private:
    explicit generator(std::coroutine_handle<promise_type> h) noexcept : h_{ h } {}

    std::coroutine_handle<promise_type> h_{};
};
