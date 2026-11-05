#include <iostream>
#include <thread>
#include <vector>

constexpr int NUM_THREADS = 4;
constexpr int INCREMENTS_PER_THREAD = 100000;

// volatile забороняє кешування у регістрах між інструкціями, але не забезпечує атомарність RMW
volatile int shared_counter = 0;

void increment_worker() {
    for (int i = 0; i < INCREMENTS_PER_THREAD; ++i) {
        // Неатомарна операція інкременту розбивається на 3 інструкції
        shared_counter++;
    }
}

int main() {
    std::vector<std::thread> threads;
    threads.reserve(NUM_THREADS);

    std::cout << "[Головний потік]: Запуск " << NUM_THREADS << " потоків...\n";

    for (int i = 0; i < NUM_THREADS; ++i) {
        threads.emplace_back(increment_worker);
    }

    for (auto& t : threads) {
        t.join();
    }

    int expected = NUM_THREADS * INCREMENTS_PER_THREAD;
    std::cout << "[Результат]: Очікувано = " << expected 
              << ", Фактично = " << shared_counter 
              << " (втрачено " << (expected - shared_counter) << " оновлень)\n";

    return 0;
}
