// C++: Порівняння швидкодії std::stable_sort проти декорованого std::sort
#include <iostream>
#include <vector>
#include <random>
#include <chrono>
#include <algorithm>

struct BenchmarkItem {
    int key;
    int payload[8]; // Навантаження пам'яті
};

int main() {
    const size_t N = 1000000;
    std::cout << "Генерація " << N << " елементів з дубльованими ключами...\n";

    std::mt19937 rng(42);
    std::uniform_int_distribution<int> dist(1, 100); // Багато однаковіх ключів (від 1 до 100)

    std::vector<BenchmarkItem> data(N);
    for (size_t i = 0; i < N; ++i) {
        data[i].key = dist(rng);
        data[i].payload[0] = static_cast<int>(i);
    }

    // Тест 1: std::stable_sort (нативний Merge/Timsort)
    {
        auto test_data = data;
        auto start = std::chrono::high_resolution_clock::now();

        std::stable_sort(test_data.begin(), test_data.end(), [](const BenchmarkItem& a, const BenchmarkItem& b) {
            return a.key < b.key;
        });

        auto end = std::chrono::high_resolution_clock::now();
        std::chrono::duration<double, std::milli> duration = end - start;
        std::cout << "Час std::stable_sort: " << duration.count() << " ms\n";
    }

    // Тест 2: Декорований std::sort (Key Augmentation + Introsort)
    {
        auto test_data = data;
        auto start = std::chrono::high_resolution_clock::now();

        struct Decorated {
            BenchmarkItem item;
            size_t orig_idx;
        };

        std::vector<Decorated> decorated(N);
        for (size_t i = 0; i < N; ++i) {
            decorated[i] = {test_data[i], i};
        }

        std::sort(decorated.begin(), decorated.end(), [](const Decorated& a, const Decorated& b) {
            if (a.item.key != b.item.key) return a.item.key < b.item.key;
            return a.orig_idx < b.orig_idx;
        });

        for (size_t i = 0; i < N; ++i) {
            test_data[i] = decorated[i].item;
        }

        auto end = std::chrono::high_resolution_clock::now();
        std::chrono::duration<double, std::milli> duration = end - start;
        std::cout << "Час декорованого std::sort: " << duration.count() << " ms\n";
    }

    return 0;
}
