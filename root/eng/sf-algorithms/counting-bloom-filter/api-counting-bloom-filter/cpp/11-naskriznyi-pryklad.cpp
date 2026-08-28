#include <iostream>
#include <string_view>

void demoCbfLifecycle() {
    // 1. Розрахунок параметрів для 100 000 ключів із похибкою 1%
    size_t cap = CountingBloomFilter::optimalCapacity(100'000, 0.01);
    uint32_t k = CountingBloomFilter::optimalHashes(cap, 100'000);

    // 2. Створення фільтра (RAII)
    CountingBloomFilter filter(cap, k);

    // 3. Додавання ключів
    std::string_view key1 = "session_token_xyz_998";
    filter.insert(key1);

    // 4. Перевірка наявності
    if (filter.contains(key1)) {
        std::cout << "Ключ знайдено!\n";
    }

    // 5. Видалення ключа
    filter.remove(key1);
}
