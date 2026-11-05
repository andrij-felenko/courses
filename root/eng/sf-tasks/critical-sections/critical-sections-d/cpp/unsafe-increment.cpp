#include <iostream>
#include <thread>
#include <vector>

constexpr int NUM_THREADS = 4;
constexpr int ITERATIONS = 1000000;

// Спільний змінюваний стан без захисту
long global_counter = 0;

void unsafe_increment() {
    for (int i = 0; i < ITERATIONS; ++i) {
        // Незахищена некомутативна операція RMW
        ++global_counter;
    }
}

int main() {
    std::vector<std::thread> threads;
    threads.reserve(NUM_THREADS);

    for (int i = 0; i < NUM_THREADS; ++i) {
        threads.emplace_back(unsafe_increment);
    }

    for (auto& t : threads) {
        t.join();
    }

    std::cout << "Фактичний результат: " << global_counter
              << " (Очікувалось: " << NUM_THREADS * ITERATIONS << ")\n";
    return 0;
}
