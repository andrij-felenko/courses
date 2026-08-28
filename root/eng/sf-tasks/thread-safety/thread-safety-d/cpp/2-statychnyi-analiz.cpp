#include <mutex>

class GuardedAccount {
public:
    void deposit(double amount) {
        std::lock_guard<std::mutex> lock(mu_);
        balance_ += amount; // OK: замок mu_ захоплено
    }

    double get_balance_unsafe() const {
        // Помилка компіляції: спроба читання balance_ без захоплення mu_!
        // return balance_; 
        std::lock_guard<std::mutex> lock(mu_);
        return balance_;
    }

private:
    mutable std::mutex mu_;
    // Атрибут guarded_by вказує компілятору на зв'язок поля із замком
    double balance_ [[clang::guarded_by(mu_)]] {0.0};
};
