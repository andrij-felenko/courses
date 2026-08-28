// C++20: Пошук у std::vector (std::lower_bound), std::map та std::unordered_map
#include <iostream>
#include <vector>
#include <map>
#include <unordered_map>
#include <algorithm>
#include <random>
#include <chrono>

int main() {
    constexpr size_t DATA_SIZE = 100'000;
    constexpr size_t LOOKUP_COUNT = 1'000'000;

    std::mt19937 rng(42);
    std::uniform_int_distribution<int32_t> dist(1, 1'000'000);

    // Створення впорядкованого вектора (аналог std::flat_map)
    std::vector<std::pair<int32_t, int32_t>> sorted_vec;
    sorted_vec.reserve(DATA_SIZE);
    for (size_t i = 0; i < DATA_SIZE; ++i) {
        sorted_vec.emplace_back(dist(rng), static_cast<int32_t>(i));
    }
    std::sort(sorted_vec.begin(), sorted_vec.end());

    // Створення std::map та std::unordered_map
    std::map<int32_t, int32_t> tree_map(sorted_vec.begin(), sorted_vec.end());
    std::unordered_map<int32_t, int32_t> hash_map(sorted_vec.begin(), sorted_vec.end());

    // Генерація ключів для пошуку
    std::vector<int32_t> lookup_keys(LOOKUP_COUNT);
    for (size_t i = 0; i < LOOKUP_COUNT; ++i) lookup_keys[i] = dist(rng);

    // 1. Пошук у std::vector через std::lower_bound
    auto t1 = std::chrono::high_resolution_clock::now();
    size_t found_vec = 0;
    for (int32_t k : lookup_keys) {
        auto it = std::lower_bound(sorted_vec.begin(), sorted_vec.end(), k,
            [](const auto& pair, int32_t val) { return pair.first < val; });
        if (it != sorted_vec.end() && it->first == k) ++found_vec;
    }
    auto t2 = std::chrono::high_resolution_clock::now();

    // 2. Пошук у std::map
    size_t found_map = 0;
    for (int32_t k : lookup_keys) {
        if (tree_map.find(k) != tree_map.end()) ++found_map;
    }
    auto t3 = std::chrono::high_resolution_clock::now();

    // 3. Пошук у std::unordered_map
    size_t found_hash = 0;
    for (int32_t k : lookup_keys) {
        if (hash_map.find(k) != hash_map.end()) ++found_hash;
    }
    auto t4 = std::chrono::high_resolution_clock::now();

    double ms_vec = std::chrono::duration<double, std::milli>(t2 - t1).count();
    double ms_map = std::chrono::duration<double, std::milli>(t3 - t2).count();
    double ms_hash = std::chrono::duration<double, std::milli>(t4 - t3).count();

    std::cout << "Sorted Vector (lower_bound): " << ms_vec << " ms (знайдено: " << found_vec << ")\n";
    std::cout << "std::map (Red-Black Tree):   " << ms_map << " ms (знайдено: " << found_map << ")\n";
    std::cout << "std::unordered_map (Hash):   " << ms_hash << " ms (знайдено: " << found_hash << ")\n";
}
