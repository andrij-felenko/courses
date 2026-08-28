#include <cstdint>
#include <mutex>

struct Account {
    int64_t balance{0};
    mutable std::mutex mtx;
};

bool transfer_cpp(Account& from, Account& to, int64_t amount) {
    // Одночасне захоплення двох замків без ризику дедлоку завдяки std::scoped_lock!
    std::scoped_lock lock(from.mtx, to.mtx);

    if (from.balance >= amount) {
        from.balance -= amount;
        to.balance += amount;
        return true;
    }
    return false;
}
