// Ідіоматична C++17/20 реалізація (RAII, variant, exception_ptr, std::shared_ptr)
#include <iostream>
#include <mutex>
#include <condition_variable>
#include <memory>
#include <variant>
#include <exception>
#include <stdexcept>
#include <thread>
#include <string>

namespace custom {

template <typename T>
class custom_future;

template <typename T>
struct shared_state {
    std::mutex mtx;
    std::condition_variable cv;
    bool ready = false;
    std::variant<std::monostate, T, std::exception_ptr> storage;
};

template <typename T>
class custom_promise {
public:
    custom_promise() : state_(std::make_shared<shared_state<T>>()) {}

    ~custom_promise() {
        if (state_) {
            std::lock_guard<std::mutex> lock(state_->mtx);
            if (!state_->ready) {
                state_->storage = std::make_exception_ptr(
                    std::runtime_error("broken_promise: promise destroyed without value")
                );
                state_->ready = true;
                state_->cv.notify_all();
            }
        }
    }

    custom_promise(const custom_promise&) = delete;
    custom_promise& operator=(const custom_promise&) = delete;

    custom_promise(custom_promise&&) noexcept = default;
    custom_promise& operator=(custom_promise&&) noexcept = default;

    custom_future<T> get_future() {
        if (!state_) {
            throw std::logic_error("no_state: promise moved or invalid");
        }
        return custom_future<T>(state_);
    }

    void set_value(T val) {
        std::unique_lock<std::mutex> lock(state_->mtx);
        if (state_->ready) {
            throw std::logic_error("promise_already_satisfied");
        }
        state_->storage = std::move(val);
        state_->ready = true;
        lock.unlock(); // Звільняємо lock перед сповіщенням для зменшення контеншну
        state_->cv.notify_all();
    }

    void set_exception(std::exception_ptr e) {
        std::unique_lock<std::mutex> lock(state_->mtx);
        if (state_->ready) {
            throw std::logic_error("promise_already_satisfied");
        }
        state_->storage = e;
        state_->ready = true;
        lock.unlock();
        state_->cv.notify_all();
    }

private:
    std::shared_ptr<shared_state<T>> state_;
};

template <typename T>
class custom_future {
public:
    custom_future() = default;

    explicit custom_future(std::shared_ptr<shared_state<T>> st) 
        : state_(std::move(st)) {}

    bool valid() const noexcept {
        return state_ != nullptr;
    }

    T get() {
        if (!state_) {
            throw std::logic_error("no_state: future is invalid");
        }

        std::unique_lock<std::mutex> lock(state_->mtx);
        state_->cv.wait(lock, [this]() { return state_->ready; });

        // Після отримання результату зробимо future невалідним (1:1)
        auto st = std::move(state_);

        if (std::holds_alternative<std::exception_ptr>(st->storage)) {
            std::rethrow_exception(std::get<std::exception_ptr>(st->storage));
        }

        return std::get<T>(std::move(st->storage));
    }

    void wait() const {
        if (!state_) throw std::logic_error("no_state");
        std::unique_lock<std::mutex> lock(state_->mtx);
        state_->cv.wait(lock, [this]() { return state_->ready; });
    }

private:
    std::shared_ptr<shared_state<T>> state_;
};

} // namespace custom
