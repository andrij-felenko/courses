// Застосування Acquire-Release у користувацькому просторі (C++17)
#include <atomic>
#include <iostream>

struct MyData {
    int value{0};
    int status{0};
};

std::atomic<int> global_ready_flag{0};
MyData payload;

// Потік 1: Виробник
void producer()
{
    payload.value = 42;
    payload.status = 1;

    // Публікація прапорця з семантикою Release
    global_ready_flag.store(1, std::memory_order_release);
}

// Потік 2: Споживач
void consumer()
{
    // Перевірка прапорця з семантикою Acquire
    if (global_ready_flag.load(std::memory_order_acquire) == 1) {
        // Гарантовано надрукує 42!
        std::cout << "Payload value: " << payload.value << "\n";
    }
}
