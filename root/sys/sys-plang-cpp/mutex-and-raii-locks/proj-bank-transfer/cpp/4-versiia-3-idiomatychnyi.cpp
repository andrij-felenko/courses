#include <mutex>
#include <iostream>
#include <vector>
#include <thread>
#include <chrono>

struct Account {
    int id;
    double balance;
    mutable std::mutex mtx;

    Account(int id_, double bal) : id(id_), balance(bal) {}
};

bool transfer_idiomatic(Account& from, Account& to, double amount) {
    // 1. Захист від самоприсвоєння: захоплення одного м'ютекса двічі є UB для std::mutex
    if (&from == &to) return false;

    // 2. Одночасне RAII-захоплення двох м'ютексів з автоматичним уникненням дедлоку
    std::scoped_lock lock(from.mtx, to.mtx);

    if (from.balance < amount) {
        return false;
    }

    from.balance -= amount;
    to.balance += amount;
    return true;
}

int main() {
    Account acc1(1, 1000.0);
    Account acc2(2, 500.0);

    std::vector<std::thread> threads;

    // Потік A: перераховує з acc1 в acc2
    for (int i = 0; i < 100; ++i) {
        threads.emplace_back(transfer_idiomatic, std::ref(acc1), std::ref(acc2), 10.0);
    }

    // Потік B: перераховує з acc2 в acc1 паралельно
    for (int i = 0; i < 100; ++i) {
        threads.emplace_back(transfer_idiomatic, std::ref(acc2), std::ref(acc1), 5.0);
    }

    for (auto& t : threads) {
        t.join();
    }

    std::cout << "Баланс рахунку 1: " << acc1.balance << " грн\n";
    std::cout << "Баланс рахунку 2: " << acc2.balance << " грн\n";
    return 0;
}
