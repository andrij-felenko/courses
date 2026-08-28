#include <iostream>

int main() {
    CuckooMap<uint64_t, uint64_t> map(16);
    constexpr uint64_t N = 10000;

    for (uint64_t k = 1; k <= N; ++k) {
        map.insert(k, k * 10);
    }

    for (uint64_t k = 1; k <= N; ++k) {
        auto val = map.find(k);
        if (!val.has_value() || *val != k * 10) {
            std::cerr << "Помилка пошуку ключа " << k << '\n';
            return 1;
        }
    }

    for (uint64_t k = 1; k <= N; k += 2) {
        map.erase(k);
    }

    for (uint64_t k = 1; k <= N; ++k) {
        auto val = map.find(k);
        if (k % 2 != 0 && val.has_value()) {
            std::cerr << "Помилка: видалений ключ " << k << " знайдено\n";
            return 1;
        }
        if (k % 2 == 0 && (!val.has_value() || *val != k * 10)) {
            std::cerr << "Помилка: збережений ключ " << k << " не знайдено\n";
            return 1;
        }
    }

    std::cout << "Усі C++ тести пройдено. Розмір: " << map.size()
              << ", Місткість: " << map.capacity() << '\n';
    return 0;
}
