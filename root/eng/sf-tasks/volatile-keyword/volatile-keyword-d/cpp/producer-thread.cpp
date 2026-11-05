#include <iostream>
#include <thread>
#include <atomic>

// volatile не гарантує впорядкованості на рівні процесорного конвеєра
volatile int payload = 0;
std::atomic<bool> ready{false};

void producer_thread() {
    payload = 42; // Підготовка даних

    // Атомарний запис із семантикою memory_order_release скидає буфери запису в залізі
    ready.store(true, std::memory_order_release);
}

void consumer_thread() {
    // Атомарне читання з семантикою memory_order_acquire гарантує впорядкованість
    while (!ready.load(std::memory_order_acquire)) {
        // Пасивне очікування
    }

    std::cout << "[Споживач]: Отримано payload = " << payload << "\n";
}

int main() {
    std::thread t1(producer_thread);
    std::thread t2(consumer_thread);

    t1.join();
    t2.join();
    return 0;
}
