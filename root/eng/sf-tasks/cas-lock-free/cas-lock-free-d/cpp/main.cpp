#include <iostream>
#include <atomic>

int main() {
    std::atomic<long> value{10};
    long expected = 10;
    long desired = 20;

    // Атомарна інструкція CAS на рівні C++11
    bool success = value.compare_exchange_strong(expected, desired);

    if (success) {
        std::cout << "CAS успішний! Нове значення: " << value.load() << "\n";
    } else {
        std::cout << "CAS невдалий. Актуальне значення у пам'яті: " << value.load() 
                  << ", нове expected: " << expected << "\n";
    }

    return 0;
}
