#include <iostream>
#include <vector>
#include <array>

class SimpleBloomFilter {
    std::array<bool, 16> bits_{};

public:
    void add(int val) {
        size_t h1 = static_cast<size_t>((val * 7 + 3) % 16);
        size_t h2 = static_cast<size_t>((val * 13 + 5) % 16);
        bits_[h1] = true;
        bits_[h2] = true;
    }

    [[nodiscard]] bool contains(int val) const {
        size_t h1 = static_cast<size_t>((val * 7 + 3) % 16);
        size_t h2 = static_cast<size_t>((val * 13 + 5) % 16);
        return bits_[h1] && bits_[h2];
    }
};

int main() {
    SimpleBloomFilter bf;
    std::cout << "=== Перевірка колізій у фільтрі Блума ===\n";
    for (int v : {1, 4, 9, 12, 15}) bf.add(v);

    int test_val = 7;
    if (bf.contains(test_val)) {
        std::cout << "Елемент " << test_val 
                  << " викликав хибне позитивне спрацьовування за принципом Діріхле!\n";
    }
    return 0;
}
