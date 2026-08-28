#include <iostream>
#include <thread>
#include <vector>

constexpr int NUM_TRANSFERS = 500000;

int main() {
    SafeAccount acc1(100000);
    SafeAccount acc2(100000);

    std::vector<std::jthread> threads;
    threads.reserve(8);

    // 4 потоки переказують з acc1 на acc2
    for (int i = 0; i < 4; ++i) {
        threads.emplace_back([&acc1, &acc2]() {
            for (int k = 0; k < NUM_TRANSFERS; ++k) {
                transfer_money(acc1, acc2, 10);
            }
        });
    }

    // 4 потоки паралельно переказують з acc2 на acc1
    for (int i = 0; i < 4; ++i) {
        threads.emplace_back([&acc1, &acc2]() {
            for (int k = 0; k < NUM_TRANSFERS; ++k) {
                transfer_money(acc2, acc1, 10);
            }
        });
    }

    // Очікуємо завершення всіх потоків
    threads.clear();

    const int64_t total = acc1.get_balance() + acc2.get_balance();
    std::cout << "Баланс 1: " << acc1.get_balance()
              << ", Баланс 2: " << acc2.get_balance()
              << ", Разом: " << total << " (Очікувалося: 200000)\n";

    return (total == 200000) ? 0 : 1;
}
