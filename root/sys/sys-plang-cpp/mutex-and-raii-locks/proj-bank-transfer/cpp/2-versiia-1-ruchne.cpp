#include <mutex>
#include <cstdint>
#include <stdexcept>

struct Account {
    int id;
    double balance;
    mutable std::mutex mtx;
};

bool transfer_cpp_manual(Account& from, Account& to, double amount) {
    if (&from == &to) return false;

    // Впорядкування адресами для запобігання дедлоку
    Account* first = &from < &to ? &from : &to;
    Account* second = &from < &to ? &to : &from;

    std::lock_guard<std::mutex> lock1(first->mtx);
    std::lock_guard<std::mutex> lock2(second->mtx);

    if (from.balance < amount) {
        return false;
    }

    from.balance -= amount;
    to.balance += amount;
    return true;
}
