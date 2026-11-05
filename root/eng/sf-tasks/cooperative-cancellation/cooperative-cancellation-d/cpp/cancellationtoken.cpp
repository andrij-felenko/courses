#include <atomic>
#include <memory>
#include <iostream>

// Потокобезпечний токен скасування в C++ тільки для читання
class CancellationToken {
private:
    std::shared_ptr<const std::atomic<bool>> flag_;

public:
    explicit CancellationToken(std::shared_ptr<const std::atomic<bool>> flag)
        : flag_(std::move(flag)) {}

    [[nodiscard]] bool is_cancellation_requested() const noexcept {
        return flag_ && flag_->load(std::memory_order_acquire);
    }
};

// Джерело скасування в C++ — ініціалізує та генерує сигнал зупинки
class CancellationTokenSource {
private:
    std::shared_ptr<std::atomic<bool>> flag_ = std::make_shared<std::atomic<bool>>(false);

public:
    CancellationTokenSource() = default;

    void cancel() noexcept {
        flag_->store(true, std::memory_order_release);
    }

    [[nodiscard]] CancellationToken get_token() const noexcept {
        return CancellationToken(flag_);
    }
};

// Робоча процедура з перевіркою точки скасування
bool run_worker_loop(CancellationToken token, int total_items) {
    for (int i = 0; i < total_items; ++i) {
        // Точка скасування (checkpoint)
        if (token.is_cancellation_requested()) {
            std::cout << "Обробку скасовано на ітерації " << i << std::endl;
            return false;
        }

        // Обробка одного елемента даних
    }
    return true;
}
