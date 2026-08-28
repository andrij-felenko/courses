#include <coroutine>
#include <exception>
#include <utility>

template<typename T>
class Generator {
public:
    struct promise_type {
        const T* current_value{nullptr};
        std::exception_ptr exception{nullptr};

        Generator get_return_object() noexcept {
            return Generator{std::coroutine_handle<promise_type>::from_promise(*this)};
        }

        // Призупиняємось одразу при створенні: лінивий старт
        std::suspend_always initial_suspend() noexcept { return {}; }
        
        // Призупиняємось при завершенні, щоб зберегти стан до виклику destroy()
        std::suspend_always final_suspend() noexcept { return {}; }

        // Обробка оператора co_yield
        std::suspend_always yield_value(const T& value) noexcept {
            current_value = std::addressof(value);
            return {};
        }

        void return_void() noexcept {}

        void unhandled_exception() noexcept {
            exception = std::current_exception();
        }
    };

    using handle_type = std::coroutine_handle<promise_type>;

    explicit Generator(handle_type h) noexcept : handle_(h) {}

    ~Generator() {
        if (handle_) {
            handle_.destroy();
        }
    }

    // Заборона копіювання для захисту від подвійного звільнення фрейму
    Generator(const Generator&) = delete;
    Generator& operator=(const Generator&) = delete;

    // Переміщення дескриптора володіння
    Generator(Generator&& other) noexcept : handle_(std::exchange(other.handle_, {})) {}
    Generator& operator=(Generator&& other) noexcept {
        if (this != &other) {
            if (handle_) handle_.destroy();
            handle_ = std::exchange(other.handle_, {});
        }
        return *this;
    }

    // Клас ітератора для інтеграції з циклами range-based for та std::ranges
    class Iterator {
    public:
        using value_type = T;
        using difference_type = std::ptrdiff_t;

        explicit Iterator(handle_type h) : handle_(h) {}

        Iterator& operator++() {
            handle_.resume();
            if (handle_.done()) {
                auto& ex = handle_.promise().exception;
                if (ex) std::rethrow_exception(ex);
            }
            return *this;
        }

        void operator++(int) { ++(*this); }

        const T& operator*() const noexcept {
            return *(handle_.promise().current_value);
        }

        bool operator==(std::default_sentinel_t) const noexcept {
            return !handle_ || handle_.done();
        }

    private:
        handle_type handle_{};
    };

    Iterator begin() {
        if (handle_) {
            handle_.resume();
            if (handle_.done()) {
                auto& ex = handle_.promise().exception;
                if (ex) std::rethrow_exception(ex);
            }
        }
        return Iterator{handle_};
    }

    std::default_sentinel_t end() const noexcept {
        return {};
    }

private:
    handle_type handle_{};
};
