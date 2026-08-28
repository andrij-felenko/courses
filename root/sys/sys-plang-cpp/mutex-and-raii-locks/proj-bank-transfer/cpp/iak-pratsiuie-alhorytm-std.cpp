#include <mutex>
#include <utility>

struct Account {
    int id;
    double balance;
    mutable std::mutex mtx;
};

bool transfer_cpp11(Account& from, Account& to, double amount) {
    if (&from == &to) return false;

    // 1. Атомарне захоплення обох м'ютексів без дедлоку
    std::lock(from.mtx, to.mtx);

    // 2. Передача керування RAII-обгорткам із тегом adopt_lock
    std::lock_guard<std::mutex> lock_from(from.mtx, std::adopt_lock);
    std::lock_guard<std::mutex> lock_to(to.mtx, std::adopt_lock);

    if (from.balance < amount) {
        return false;
    }

    from.balance -= amount;
    to.balance += amount;
    return true;
}
