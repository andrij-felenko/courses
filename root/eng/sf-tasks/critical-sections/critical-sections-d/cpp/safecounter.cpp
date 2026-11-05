#include <iostream>
#include <mutex>
#include <thread>
#include <vector>

constexpr int NUM_THREADS = 4;
constexpr int ITERATIONS = 1000000;

class SafeCounter {
private:
    long counter_ = 0;
    mutable std::mutex mutex_;

public:
    void increment() {
        for (int i = 0; i < ITERATIONS; ++i) {
            // Вхід у критичну секцію через RAII-обгортку std::lock_guard
            // Просторові межі збігаються із зоною видимості блоку lock
            std::lock_guard<std::mutex> lock(mutex_);

            // Захищена неподільна операція над спільним станом
            ++counter_;
            // Автоматичний вихід з критичної секції при знищенні об'єкта lock
        }
    }

    long value() const {
        std::lock_guard<std::mutex> lock(mutex_);
        return counter_;
    }
};

int main() {
    SafeCounter counter;
    std::vector<std::thread> threads;
    threads.reserve(NUM_THREADS);

    for (int i = 0; i < NUM_THREADS; ++i) {
        threads.emplace_back([&counter]() { counter.increment(); });
    }

    for (auto& t : threads) {
        t.join();
    }

    std::cout << "Результат захищеної критичної секції: " << counter.value()
              << " (Очікувалось: " << NUM_THREADS * ITERATIONS << ")\n";
    return 0;
}
