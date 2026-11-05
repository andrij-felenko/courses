#include <iostream>
#include <vector>
#include <thread>

constexpr int NUM_THREADS = 4;
constexpr int INCREMENTS_PER_THREAD = 1000000;

// Спільна змінна лічильника
long shared_counter = 0;

void count_unsynchronized() {
    for (int i = 0; i < INCREMENTS_PER_THREAD; ++i) {
        // Операція розбивається на декілька інструкцій ассемблера
        shared_counter++;
    }
}

int main() {
    std::vector<std::thread> threads;
    threads.reserve(NUM_THREADS);

    for (int i = 0; i < NUM_THREADS; ++i) {
        threads.emplace_back(count_unsynchronized);
    }

    for (auto& t : threads) {
        t.join();
    }

    std::cout << "Фактичне значення лічильника: " << shared_counter 
              << " (Очікувалося: " << NUM_THREADS * INCREMENTS_PER_THREAD << ")\n";
    return 0;
}
