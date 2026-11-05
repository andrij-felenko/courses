#include <iostream>
#include <thread>
#include <atomic>

// Атомарні змінні замість volatile забезпечують і атомарність, і впорядкованість
std::atomic<bool> data_ready{false};
std::atomic<int> event_counter{0};
int shared_payload = 0;

void producer_thread() {
    shared_payload = 42; // Підготовка даних

    // Атомарний запис із семантикою release створює бар'єр впорядкування
    data_ready.store(true, std::memory_order_release);

    // Атомарний інкремент запобігає втраченим оновленням
    event_counter.fetch_add(1, std::memory_order_relaxed);
}

void consumer_thread() {
    // Атомарна перевірка з семантикою acquire гарантує видимість shared_payload
    while (!data_ready.load(std::memory_order_acquire)) {
        // Пасивне очікування
    }

    std::cout << "[Споживач C++11]: Прочитано payload = " << shared_payload
              << ", всього подій = " << event_counter.load() << "\n";
}

int main() {
    std::thread t1(producer_thread);
    std::thread t2(consumer_thread);

    t1.join();
    t2.join();
    return 0;
}
