#include <cstdint>
#include <mutex>

class SafeAccount {
public:
    explicit SafeAccount(int64_t initial_balance = 0) noexcept
        : balance_(initial_balance) {}

    void deposit(int64_t amount) {
        // std::lock_guard гарантує звільнення замка в деструкторі
        std::lock_guard<std::mutex> guard(mutex_);
        balance_ += amount;
    }

    bool withdraw(int64_t amount) {
        std::lock_guard<std::mutex> guard(mutex_);
        if (balance_ >= amount) {
            balance_ -= amount;
            return true;
        }
        return false;
    }

    int64_t get_balance() const {
        std::lock_guard<std::mutex> guard(mutex_);
        return balance_;
    }

    std::mutex& get_mutex() const noexcept {
        return mutex_;
    }

    // Внутрішні методи для складених операцій (викликати виключно під захопленим замком)
    int64_t raw_balance() const noexcept { return balance_; }
    void raw_modify(int64_t delta) noexcept { balance_ += delta; }

private:
    int64_t balance_{0};
    mutable std::mutex mutex_;
};
