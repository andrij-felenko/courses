#include <iostream>
#include <mutex>
#include <cstdint>
#include <memory>
#include <system_error>

class Account {
public:
    Account(uint64_t id, int64_t initial_balance)
        : id_(id), balance_(initial_balance) {}

    uint64_t id() const noexcept { return id_; }
    int64_t balance() const noexcept {
        std::lock_guard<std::mutex> lock(mtx_);
        return balance_;
    }

    // Дружня функція для виконання атомарного переказу
    friend bool transfer_money(Account& from, Account& to, int64_t amount);

private:
    uint64_t id_;
    int64_t balance_;
    mutable std::mutex mtx_;
};

// Безпечний переказ коштів у C++17.
// std::scoped_lock автоматично реалізує алгоритм уникнення дедлоків
// (Deadlock Avoidance Algorithm) для довільної кількості м'ютексів
// та звільняє їх за принципом RAII.
bool transfer_money(Account& from, Account& to, int64_t amount) {
    if (&from == &to || amount <= 0) {
        return (&from == &to); // Захист від подвійного взяття одного м'ютекса
    }

    // Захоплюємо обидва замки атомарно без ризику дедлоку.
    // std::scoped_lock внутрішньо використовує std::lock, який впорядковує
    // виклики або відкочує захоплення через try_lock при колізії.
    std::scoped_lock lock(from.mtx_, to.mtx_);

    if (from.balance_ < amount) {
        return false;
    }

    from.balance_ -= amount;
    to.balance_ += amount;
    return true;
}
