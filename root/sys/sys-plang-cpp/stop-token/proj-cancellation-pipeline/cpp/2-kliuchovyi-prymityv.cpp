#include <condition_variable>
#include <deque>
#include <mutex>
#include <optional>
#include <stop_token>
#include <utility>

template <typename T>
class InterruptibleQueue {
public:
    explicit InterruptibleQueue(std::size_t capacity)
        : capacity_(capacity) {}

    // Додавання елемента з можливістю переривання через stop_token
    bool push(T item, std::stop_token stoken) {
        std::unique_lock lock(mutex_);

        // Чекаємо, доки з'явиться вільне місце АБО надійде сигнал зупинки
        const bool not_full = cv_not_full_.wait(
            lock, 
            stoken, 
            [this] { return queue_.size() < capacity_; }
        );

        // Якщо очікування перервано сигналом зупинки і місця так і немає
        if (stoken.stop_requested() && queue_.size() >= capacity_) {
            return false;
        }

        if (!not_full) {
            return false;
        }

        queue_.push_back(std::move(item));

        // Сповіщаємо один потік-споживач, що очікує на читання
        cv_not_empty_.notify_one();
        return true;
    }

    // Витягування елемента з можливістю переривання через stop_token
    std::optional<T> pop(std::stop_token stoken) {
        std::unique_lock lock(mutex_);

        // Чекаємо наявності даних АБО сигналу зупинки
        const bool has_data = cv_not_empty_.wait(
            lock, 
            stoken, 
            [this] { return !queue_.empty(); }
        );

        if (!queue_.empty()) {
            T item = std::move(queue_.front());
            queue_.pop_front();

            // Сповіщаємо потік-виробник, що очікував вільного місця
            cv_not_full_.notify_one();
            return item;
        }

        // Черга порожня і надійшов сигнал скасування
        return std::nullopt;
    }

    // Неблокуюча перевірка поточного розміру черги
    [[nodiscard]] std::size_t size() const {
        std::lock_guard lock(mutex_);
        return queue_.size();
    }

    // Перевірка, чи порожня черга
    [[nodiscard]] bool empty() const {
        std::lock_guard lock(mutex_);
        return queue_.empty();
    }

    // Примусове сповіщення всіх очікуючих потоків (для фази дренажування)
    void notify_all() {
        cv_not_empty_.notify_all();
        cv_not_full_.notify_all();
    }

private:
    const std::size_t capacity_;
    std::deque<T> queue_;
    mutable std::mutex mutex_;
    std::condition_variable_any cv_not_empty_;
    std::condition_variable_any cv_not_full_;
};
