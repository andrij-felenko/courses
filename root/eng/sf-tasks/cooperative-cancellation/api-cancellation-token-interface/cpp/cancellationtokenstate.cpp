#include <iostream>
#include <atomic>
#include <thread>
#include <chrono>
#include <memory>

// Внутрішній стан скасування з атомарним прапорцем
class CancellationTokenState {
public:
    void cancel() noexcept {
        cancelled_.store(true, std::memory_order_release);
    }

    bool is_cancellation_requested() const noexcept {
        return cancelled_.load(std::memory_order_acquire);
    }

private:
    std::atomic<bool> cancelled_{false};
};

// Токен скасування з доступом «лише для читання»
class CancellationToken {
public:
    explicit CancellationToken(std::shared_ptr<CancellationTokenState> state)
        : state_(std::move(state)) {}

    bool is_cancellation_requested() const noexcept {
        return state_ && state_->is_cancellation_requested();
    }

private:
    std::shared_ptr<CancellationTokenState> state_;
};

// Джерело ініціації скасування
class CancellationTokenSource {
public:
    CancellationTokenSource()
        : state_(std::make_shared<CancellationTokenState>()) {}

    CancellationToken get_token() const {
        return CancellationToken(state_);
    }

    void cancel() {
        if (state_) {
            state_->cancel();
        }
    }

private:
    std::shared_ptr<CancellationTokenState> state_;
};

// Фонова обчислювальна задача
void run_worker(CancellationToken token) {
    std::cout << "[C++ Worker] Обчислювальний процес розпочато.\n";

    for (int i = 0; i < 50; ++i) {
        // Контрольна точка скасування
        if (token.is_cancellation_requested()) {
            std::cout << "[C++ Worker] Отримано запит скасування на ітерації " << i << ".\n";
            std::cout << "[C++ Worker] Вивільнення ресурсів та безпечний вихід.\n";
            return;
        }

        std::this_thread::sleep_for(std::chrono::milliseconds(15));
    }

    std::cout << "[C++ Worker] Процес успішно завершено.\n";
}
